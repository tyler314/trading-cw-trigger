from abc import ABC, abstractmethod
import datetime
import pytz
from dto.options import VerticalSpread
from utils.common_utils import OrderType, Instruction, AssetType, OptionLeg, OptionType
from tda_api.broker import place_option_spread_order

ROUNDING_PRECISION = 0.05


class Strategy(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @property
    @abstractmethod
    def order_type(self) -> OrderType:
        pass

    @property
    @abstractmethod
    def price(self) -> float:
        pass

    @property
    @abstractmethod
    def long_leg(self) -> OptionLeg:
        pass

    @property
    @abstractmethod
    def short_leg(self) -> OptionLeg:
        pass

    @property
    @abstractmethod
    def asset_type(self) -> AssetType:
        pass

    @property
    @abstractmethod
    def quantity(self) -> int:
        pass


class Dte1(Strategy):
    CONSECUTIVE_DAYS = 1
    ATR_MULTIPLIER = 1.4
    _DTE = 1
    _QUANTITY = 1

    def __init__(
        self,
        ticker: str = "SPX",
        order_type: OrderType = OrderType.CREDIT,
        buying_power: int = 500,
    ):
        self._long_leg = None
        self._short_leg = None
        self.buying_power = buying_power
        self.vs = VerticalSpread(
            ticker, self._QUANTITY, order_type, self._get_expiration_date()
        )
        self._option_type = self._get_option_type()
        (
            self._short_leg_strike,
            self._long_leg_strike,
        ) = self._calc_short_and_long_leg_strikes()
        self._price = self._calculate_price()

    @property
    def order_type(self) -> OrderType:
        return self.vs.order_type

    @property
    def price(self) -> float:
        return self._price

    @property
    def short_leg(self) -> OptionLeg:
        if self._short_leg is None:
            metadata = None
            if self._option_type == OptionType.CALL:
                metadata = self.vs.call_map[str(self._short_leg_strike)][0]
            elif self._option_type == OptionType.PUT:
                metadata = self.vs.put_map[str(self._short_leg_strike)][0]
            self._short_leg = OptionLeg(
                symbol=metadata["symbol"],
                instruction=Instruction.SELL_TO_OPEN,
                quantity=1,
                metadata=metadata,
            )
        return self._short_leg

    @property
    def long_leg(self) -> OptionLeg:
        if self._long_leg is None:
            metadata = None
            if self._option_type == OptionType.CALL:
                metadata = self.vs.call_map[str(self._long_leg_strike)][0]
            if self._option_type == OptionType.PUT:
                metadata = self.vs.put_map[str(self._long_leg_strike)][0]
            self._long_leg = OptionLeg(
                symbol=metadata["symbol"],
                instruction=Instruction.BUY_TO_OPEN,
                quantity=1,
                metadata=metadata,
            )
        return self._long_leg

    @property
    def asset_type(self) -> AssetType:
        return AssetType.OPTION

    @property
    def quantity(self) -> int:
        return self.vs.quantity

    def execute(self) -> None:
        response = {"code": "bad", "oder_body": "Null"}
        if self._option_type != OptionType.NO_OP:
            response = place_option_spread_order(
                order_type=self.order_type,
                price=self.price,
                asset_type=self.asset_type,
                long_leg=self.long_leg,
                short_leg=self.short_leg,
            )
        print(response)

    @property
    def dte(self) -> int:
        def is_friday():
            return datetime.date.today().weekday() == 4

        if is_friday():
            return self._DTE + 2
        return self._DTE

    def _get_expiration_date(self) -> datetime:
        day = datetime.datetime.now(pytz.timezone('US/Eastern')) + datetime.timedelta(hours=24 * self.dte)
        return day  # "2022-02-28"

    def _calculate_price(self) -> float:
        if self._option_type == OptionType.NO_OP:
            return -1
        long_leg_price = (
            self.long_leg.metadata["bid"] + self.long_leg.metadata["ask"]
        ) / 2.0
        short_leg_price = (
            self.short_leg.metadata["bid"] + self.short_leg.metadata["ask"]
        ) / 2.0
        price = (
            int((short_leg_price - long_leg_price) / ROUNDING_PRECISION)
            * ROUNDING_PRECISION
            + ROUNDING_PRECISION
        )
        return round(price, 2)

    def _get_option_type(self):
        def consecutive_red_days() -> bool:
            for i in range(self.CONSECUTIVE_DAYS):
                if self.vs.stock.candles[i].close >= self.vs.stock.candles[i].open:
                    return False
            return True

        def consecutive_green_days() -> bool:
            for i in range(self.CONSECUTIVE_DAYS):
                if self.vs.stock.candles[i].open >= self.vs.stock.candles[i].close:
                    return False
            return True

        if consecutive_red_days():
            return OptionType.PUT
        if consecutive_green_days():
            return OptionType.CALL
        return OptionType.NO_OP

    def _calc_short_and_long_leg_strikes(self) -> (float, float):
        def get_long_leg_strike(
            strikes: list, strike_index: int, short_strike: float
        ) -> float:
            if self._option_type == OptionType.CALL:
                for j in range(strike_index + 1, len(strikes)):
                    if abs(float(strikes[j]) - short_strike) >= self.buying_power / 100:
                        if (
                            abs(float(strikes[j]) - short_strike)
                            > self.buying_power / 100
                        ):
                            return float(strike_prices[j - 1])
                        return float(strike_prices[j])
            elif self._option_type == OptionType.PUT:
                for j in range(strike_index - 1, -1, -1):
                    if abs(float(strikes[j]) - short_strike) >= self.buying_power / 100:
                        if (
                            abs(float(strikes[j]) - short_strike)
                            > self.buying_power / 100
                        ):
                            return float(strike_prices[j + 1])
                        return float(strike_prices[j])
            return -1
        short_leg_strike = -1
        rough_strike = -1
        strike_prices = list()
        short_strike_index = -1
        if self._option_type == OptionType.CALL:
            rough_strike = (
                self.vs.stock.candles[0].close + self.vs.stock.atr * self.ATR_MULTIPLIER
            )
            strike_prices = sorted(self.vs.call_map.keys())
        elif self._option_type == OptionType.PUT:
            rough_strike = (
                self.vs.stock.candles[0].close - self.vs.stock.atr * self.ATR_MULTIPLIER
            )
            strike_prices = sorted(self.vs.put_map.keys())
        elif self._option_type == OptionType.NO_OP:
            return -1, -1

        min_diff = float("Inf")
        for i, strike in enumerate(strike_prices):
            diff = abs(float(strike) - rough_strike)
            if diff < min_diff:
                short_strike_index = i
                min_diff = diff
                short_leg_strike = float(strike)

        return short_leg_strike, get_long_leg_strike(
            strikes=strike_prices,
            strike_index=short_strike_index,
            short_strike=short_leg_strike,
        )
