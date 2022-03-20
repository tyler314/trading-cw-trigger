import datetime

from pytz import timezone

from dto.factories.option_factory import OptionFactory
from strategies.strategy import Strategy
from tda_api.broker import Broker
from utils.common_utils import OrderType, OptionType, AssetType


class Dte1(Strategy):
    ROUNDING_PRECISION = 0.05
    DTE = 1
    # -1 represents default value
    DAYS_IN_ROW_TO_DELTA = {
        OptionType.CALL: {-1: 1.0, 0: 1.8, 1: 1.6, 2: 1.2, 3: 1.1, 4: 1.1,},
        OptionType.PUT: {-1: 1.0, 0: 2.0, 1: 1.8, 2: 1.4, 3: 1.3, 4: 1.0,},
    }

    def __init__(
        self,
        ticker: str = "SPX",
        order_type: OrderType = OrderType.CREDIT,
        buying_power: int = 500,
        monday_quantity: int = 1,
        wednesday_quantity: int = 1,
        friday_quantity: int = 1,
    ):
        self._monday_quantity = monday_quantity
        self._wednesday_quantity = wednesday_quantity
        self._friday_quantity = friday_quantity
        self._broker = Broker()
        self._buying_power = buying_power
        self.option_factory = OptionFactory(
            ticker, self._quantity, order_type, self._expiration_date
        )
        self._option_type = self._get_option_type()
        self._vs = self.option_factory.get_vertical_spread(
            self._short_leg_strike_price, buying_power, self._option_type
        )

    def execute(self) -> dict:
        if self._option_type != OptionType.NO_OP:
            return self._broker.place_option_spread_order(
                order_type=self._vs.order_type,
                price=self._vs.price,
                asset_type=self.asset_type,
                long_leg=self._vs.long_leg,
                short_leg=self._vs.short_leg,
            )
        return {"code": "bad", "order_body": "Null"}

    @property
    def asset_type(self) -> AssetType:
        return AssetType.OPTION

    @property
    def _quantity(self) -> int:
        if self._is_friday():
            return self._monday_quantity
        elif self._is_tuesday():
            return self._wednesday_quantity
        elif self._is_thursday():
            return self._friday_quantity
        return 1

    @property
    def _atr_multiplier(self) -> float:
        def get_multiplier(option_map: dict, cnt: int) -> float:
            if cnt not in option_map.keys():
                return option_map[-1]
            return option_map[cnt]

        if self._option_type == OptionType.CALL:
            return get_multiplier(
                self.DAYS_IN_ROW_TO_DELTA[OptionType.CALL], self._consecutive_green_days
            )
        elif self._option_type == OptionType.PUT:
            return get_multiplier(
                self.DAYS_IN_ROW_TO_DELTA[OptionType.PUT], self._consecutive_red_days
            )
        return -1

    @property
    def _dte(self) -> int:
        if self._is_friday():
            return self.DTE + 2
        return self.DTE

    @property
    def _expiration_date(self) -> datetime:
        day = datetime.datetime.now(timezone("US/Eastern")) + datetime.timedelta(
            hours=24 * self._dte
        )
        return day

    @property
    def _consecutive_red_days(self) -> int:
        cnt = 0
        while (
            self.option_factory.stock.candles[cnt].close
            < self.option_factory.stock.candles[cnt].open
        ):
            cnt += 1
        return cnt

    @property
    def _consecutive_green_days(self) -> int:
        cnt = 0
        while (
            self.option_factory.stock.candles[cnt].open
            < self.option_factory.stock.candles[cnt].close
        ):
            cnt += 1
        return cnt

    @property
    def _short_leg_strike_price(self) -> float:
        close_price = self.option_factory.stock.candles[0].close
        delta = self.option_factory.stock.atr * self._atr_multiplier
        if self._option_type == OptionType.CALL:
            close_price += delta
        elif self._option_type == OptionType.PUT:
            close_price -= delta
        return close_price

    def _get_option_type(self) -> OptionType:
        if self._consecutive_green_days > 0:
            return OptionType.CALL
        elif self._consecutive_red_days > 0:
            return OptionType.PUT
        return OptionType.NO_OP
