from abc import ABC, abstractmethod
from dto.option import VerticalSpread
from utils.common_utils import OrderType, Instruction, AssetType, OptionLeg, OptionType
from tda_api.broker import place_option_spread_order


ROUNDING_PRECISION = 0.05


class Strategy(ABC):
    @abstractmethod
    def execute(self):
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
    CONSECUTIVE_DAYS = 3
    ATR_MULTIPLIER = 1.4
    DELTA = 10
    SPREAD_WIDTH = 10

    def __init__(
        self,
        ticker: str = "SPX",
        quantity: int = 1,
        order_type: OrderType = OrderType.CREDIT,
    ):
        self.vs = VerticalSpread(ticker, quantity, order_type)
        self._long_leg = None
        self._short_leg = None
        self._option_type = None
        self._short_leg_strike: float = self._calc_short_leg_strike()
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
            if self._are_consecutive_green_days:
                metadata = self.vs.put_map[str(self._short_leg_strike)][0]
            elif self._are_consecutive_red_days:
                metadata = self.vs.put_map[str(self._short_leg_strike)][0]
            self._short_leg = OptionLeg(
                symbol=metadata["symbol"], instruction=Instruction.SELL_TO_OPEN, quantity=1, metadata=metadata
            )
        return self._short_leg

    @property
    def long_leg(self) -> OptionLeg:
        if self._long_leg is None:
            metadata = None
            if self._are_consecutive_green_days:
                metadata = self.vs.put_map[
                    str(self._short_leg_strike + self.SPREAD_WIDTH)
                ][0]
            if self._are_consecutive_red_days:
                metadata = self.vs.put_map[
                    str(self._short_leg_strike - self.SPREAD_WIDTH)
                ][0]
            self._long_leg = OptionLeg(
                symbol=metadata["symbol"], instruction=Instruction.BUY_TO_OPEN, quantity=1, metadata=metadata
            )
        return self._long_leg

    @property
    def asset_type(self) -> AssetType:
        return AssetType.OPTION

    @property
    def quantity(self) -> int:
        return self.vs.quantity

    def execute(self):
        if self._are_consecutive_red_days or self._are_consecutive_green_days:
            return place_option_spread_order(
                order_type=self.order_type,
                price=self.price,
                asset_type=self.asset_type,
                long_leg=self.long_leg,
                short_leg=self.short_leg,
            )

    def _calculate_price(self):
        if self._are_consecutive_green_days or self._are_consecutive_red_days:
            long_leg_price = (self.long_leg.metadata['bid'] + self.long_leg.metadata['ask']) / 2.
            short_leg_price = (self.short_leg.metadata['bid'] + self.short_leg.metadata['ask']) / 2.
            price = int((short_leg_price - long_leg_price) / ROUNDING_PRECISION) * ROUNDING_PRECISION + ROUNDING_PRECISION
            return round(price, 2)
        return -1

    @property
    def _are_consecutive_red_days(self) -> bool:
        for i in range(1):
            if self.vs.stock.candles[i].close >= self.vs.stock.candles[i].open:
                return False
        return True

    @property
    def _are_consecutive_green_days(self) -> bool:
        for i in range(1):
            if self.vs.stock.candles[i].open >= self.vs.stock.candles[i].close:
                return False
        return True

    def _calc_short_leg_strike(self) -> float:
        if self._are_consecutive_green_days:
            return (
                (
                    (
                        self.vs.stock.candles[0].close
                        + self.vs.stock.atr * self.ATR_MULTIPLIER
                    )
                    // 10
                )
                * 10
            ) + self.DELTA
        elif self._are_consecutive_red_days:
            return (
                (
                    self.vs.stock.candles[0].close
                    - self.vs.stock.atr * self.ATR_MULTIPLIER
                )
                // 10
            ) * 10 - self.DELTA
        return self.vs.stock.candles[0].close
