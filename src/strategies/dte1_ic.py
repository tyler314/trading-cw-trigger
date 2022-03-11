from strategies.dte1 import Dte1
from utils.common_utils import OrderType, OptionType


class Dte1IC(Dte1):
    def __init__(
        self,
        ticker: str = "SPX",
        order_type: OrderType = OrderType.CREDIT,
        buying_power: int = 500,
    ):
        super().__init__(ticker, order_type, buying_power)
        if self._option_type == OptionType.PUT:
            self._option_type = OptionType.CALL
        elif self._option_type == OptionType.CALL:
            self._option_type = OptionType.PUT

    def execute(self) -> dict:
        super().execute()
        (
            self._short_leg_strike,
            self._long_leg_strike,
        ) = self._calc_short_and_long_leg_strikes()
        self._long_leg = self._get_long_leg()
        self._short_leg = self._get_short_leg()
        self._price = self._calculate_price()
        return super().execute()
