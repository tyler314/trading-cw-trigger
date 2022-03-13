import datetime

from pytz import timezone

from factories.option_factory import OptionFactory
from strategies.strategy import Strategy
from tda_api.broker import Broker
from utils.common_utils import OrderType, OptionType, AssetType


class Dte1(Strategy):
    CALL_ATR_MULTIPLIER = 1
    PUT_ATR_MULTIPLIER = 1
    _ROUNDING_PRECISION = 0.05
    _DTE = 1

    def __init__(
        self,
        ticker: str = "SPX",
        order_type: OrderType = OrderType.CREDIT,
        buying_power: int = 500,
        monday_quantity: int = 1,
        wednesday_quantity: int = 1,
        friday_quantity: int = 1,
    ):
        self._broker = Broker()
        self._buying_power = buying_power
        self.option_factory = OptionFactory(
            ticker, self._get_quantity(), order_type, self._get_expiration_date()
        )
        self._option_type = self._get_option_type()
        self._vs = self.option_factory.get_vertical_spread(
            self._get_rough_strike_price(), buying_power, self._option_type
        )
        self._monday_quantity = monday_quantity
        self._wednesday_quantity = wednesday_quantity
        self._friday_quantity = friday_quantity

    def execute(self) -> dict:
        response = {"code": "bad", "order_body": "Null"}
        if self._option_type != OptionType.NO_OP:
            response = self._broker.place_option_spread_order(
                order_type=self._vs.order_type,
                price=self._vs.price,
                asset_type=self.asset_type,
                long_leg=self._vs.long_leg,
                short_leg=self._vs.short_leg,
            )
        return response

    @property
    def asset_type(self) -> AssetType:
        return AssetType.OPTION

    def _get_quantity(self) -> int:
        if self._is_friday():
            return self._monday_quantity
        elif self._is_tuesday():
            return self._wednesday_quantity
        elif self._is_thursday():
            return self._friday_quantity
        return 1

    @property
    def _adjusted_atr_multiplier(self) -> float:
        multiplier = 0
        if self._option_type == OptionType.CALL:
            green_cnt = self._get_consecutive_green_days()
            multiplier = self.CALL_ATR_MULTIPLIER
            if green_cnt == 0:
                multiplier += 0.8
            elif green_cnt == 1:
                multiplier += 0.6
            elif green_cnt == 2:
                multiplier += 0.2
            elif green_cnt == 3:
                multiplier += 0.1
            elif green_cnt == 4:
                multiplier += 0.1
        elif self._option_type == OptionType.PUT:
            red_cnt = self._get_consecutive_red_days()
            multiplier = self.PUT_ATR_MULTIPLIER
            if red_cnt == 0:
                multiplier += 1.0
            elif red_cnt == 1:
                multiplier += 0.8
            elif red_cnt == 2:
                multiplier += 0.4
            elif red_cnt == 3:
                multiplier += 0.3
            elif red_cnt == 4:
                multiplier += 0.0
        return multiplier

    @property
    def _dte(self) -> int:
        if self._is_friday():
            return self._DTE + 2
        return self._DTE

    def _get_expiration_date(self) -> datetime:
        day = datetime.datetime.now(timezone("US/Eastern")) + datetime.timedelta(
            hours=24 * self._dte
        )
        return day  # "2022-02-28"

    def _get_consecutive_red_days(self):
        cnt = 0
        while (
            self.option_factory.stock.candles[cnt].close
            < self.option_factory.stock.candles[cnt].open
        ):
            cnt += 1
        return cnt

    def _get_consecutive_green_days(self):
        cnt = 0
        while (
            self.option_factory.stock.candles[cnt].open
            < self.option_factory.stock.candles[cnt].close
        ):
            cnt += 1
        return cnt

    def _get_option_type(self):
        if self._get_consecutive_green_days() > 0:
            return OptionType.CALL
        elif self._get_consecutive_red_days() > 0:
            return OptionType.PUT
        return OptionType.NO_OP

    def _get_rough_strike_price(self):
        rough_strike = -1
        if self._option_type == OptionType.CALL:
            rough_strike = (
                self._vs.stock.candles[0].close
                + self._vs.stock.atr * self._adjusted_atr_multiplier
            )
        elif self._option_type == OptionType.PUT:
            rough_strike = (
                self.option_factory.stock.candles[0].close
                - self.option_factory.stock.atr * self._adjusted_atr_multiplier
            )
        return rough_strike
