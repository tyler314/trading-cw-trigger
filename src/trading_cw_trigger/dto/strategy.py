from abc import ABC, abstractmethod
from dto.option import OrderType, VerticalSpread, OptionLeg, Instruction


class Strategy(ABC):

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    @property
    def order_type(self):
        pass

    @abstractmethod
    @property
    def price(self):
        pass

    @abstractmethod
    @property
    def long_leg(self):
        pass

    @abstractmethod
    @property
    def short_leg(self):
        pass

    @abstractmethod
    @property
    def asset_type(self):
        pass

    @abstractmethod
    @property
    def quantity(self):
        pass


class Dte1(Strategy):
    CONSECUTIVE_DAYS = 3
    ATR_MULTIPLIER = 1.4
    DELTA = 10
    SPREAD_WIDTH = 10

    def __init__(self, ticker: str = "SPX", quantity: int = 1, order_type: OrderType = OrderType.CREDIT):
        self.vs = VerticalSpread(ticker, quantity, 0.5, order_type)
        self._long_leg = None
        self._short_leg = None
        self._strike = self.vs.stock.candles[0].close

    @property
    def _are_consecutive_red_days(self):
        for i in range(self.CONSECUTIVE_DAYS):
            if self.vs.stock.candles[i].close >= self.vs.stock.candles[i].open:
                return False
        return True

    @property
    def _are_consecutive_green_days(self):
        for i in range(self.CONSECUTIVE_DAYS):
            if self.vs.stock.candles[i].open >= self.vs.stock.candles[i].close:
                return False
        return True

    def _sell_put_spread(self):
        pass

    @property
    def order_type(self):
        return self.vs.order_type.value

    @property
    def price(self):
        return str(round(self.vs.price, 2))

    @property
    def long_leg(self):
        if self._long_leg is None:
            symbol = None
            if self._are_consecutive_green_days:
                self._strike = (((self.vs.stock.candles[0].close + self.vs.stock.atr * self.ATR_MULTIPLIER) // 10) * 10) + self.DELTA
                symbol = self.vs.put_map[str(self._strike)][0]['symbol']
            elif self._are_consecutive_red_days:
                self._strike = ((self.vs.stock.candles[0].close - self.vs.stock.atr * self.ATR_MULTIPLIER) // 10) * 10 - self.DELTA
                symbol = self.vs.put_map[str(self._strike)][0]['symbol']
            self._long_leg = OptionLeg(symbol=symbol, instruction=Instruction.SELL_TO_OPEN, quantity=1)
        return self._long_leg

    @property
    def short_leg(self):
        if self._short_leg is None:
            if self._are_consecutive_green_days:
                symbol = self.vs.put_map[str(self._strike + self.SPREAD_WIDTH)][0]['symbol']
            if self._are_consecutive_red_days:
                symbol = self.vs.put_map[str(self._strike - self.SPREAD_WIDTH)][0]['symbol']
            self._short_leg = OptionLeg(symbol=symbol, instruction=Instruction.BUY_TO_OPEN, quantity=1)
        return self._short_leg

    @property
    def asset_type(self):
        return "OPTION"

    @property
    def quantity(self):
        return self.vs.quantity


    # def execute(self):
    #     if self._are_consecutive_red_days():
    #         self._sell_put_spread()
    #     elif self._are_consecutive_green_days():
    #         self._sell_call_spread()
