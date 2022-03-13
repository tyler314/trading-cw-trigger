from strategies.dte1 import Dte1
from utils.common_utils import OrderType, OptionType


class Dte1IC(Dte1):
    def __init__(
        self,
        ticker: str = "SPX",
        order_type: OrderType = OrderType.CREDIT,
        buying_power: int = 500,
        monday_quantity: int = 1,
        wednesday_quantity: int = 1,
        friday_quantity: int = 1,
    ):
        super().__init__(
            ticker,
            order_type,
            buying_power,
            monday_quantity,
            wednesday_quantity,
            friday_quantity,
        )
        if self._option_type == OptionType.PUT:
            self._option_type = OptionType.CALL
        elif self._option_type == OptionType.CALL:
            self._option_type = OptionType.PUT

    def execute(self) -> dict:
        super().execute()
        self._vs = self.option_factory.get_vertical_spread(
            self._get_rough_strike_price(), self._buying_power, self._option_type
        )
        return super().execute()
