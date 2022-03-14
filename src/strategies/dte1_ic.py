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

    def execute(self) -> dict:
        response = super().execute()
        self._option_type = (
            OptionType.CALL if self._option_type == OptionType.PUT else OptionType.PUT
        )
        self._vs = self.option_factory.get_vertical_spread(
            self._short_leg_strike_price, self._buying_power, self._option_type,
        )
        return {"order 1": super().execute(), "order 2": response}
