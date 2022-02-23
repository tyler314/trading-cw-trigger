import datetime
from enum import Enum
from dataclasses import dataclass
from utils.common_utils import transform_ticker, TradingPlatforms
from tda_api.broker import option_chain
from dto.stock import Stock


class OrderType(Enum):
    CREDIT = "NET_CREDIT"
    DEBIT = "NET_DEBIT"

class Instruction(Enum):
    BUY_TO_OPEN = "BUY_TO_OPEN"
    SELL_TO_OPEN = "SELL_TO_OPEN"
    BUY_TO_CLOSE = "BUY_TO_CLOSE"
    SELL_TO_CLOSE = "SELL_TO_CLOSE"


class VerticalSpread:
    def __init__(
        self,
        ticker: str,
        quantity: int,
        price: float,
        order_type: OrderType,
        expiration_date: datetime.date = None,
        dte: int = 1,
    ):
        self.order_type = order_type
        self.dte = dte
        self.stock = Stock(ticker)
        self.quantity = quantity
        self.price = price
        if expiration_date is None:
            self.expiration_date = self._get_expiration_date()
        else:
            self.expiration_date = expiration_date.strftime("%Y-%m-%d")
        (
            self.put_map,
            self.call_map,
        ) = self._get_put_and_call_maps()  # maps strike-price -> metadata

    def _get_expiration_date(self):
        day = datetime.date.today() + datetime.timedelta(hours=24 * self.dte)
        return day.strftime("%Y-%m-%d")  # YYYY-MM-DD format

    def _get_put_and_call_maps(self) -> (dict, dict):
        options = option_chain(
            transform_ticker(self.stock.ticker, TradingPlatforms.TDA)
        )
        put_exp_map = options["putExpDateMap"]
        call_exp_map = options["callExpDateMap"]
        put_option = None
        call_option = None
        for key in put_exp_map.keys():
            if self.expiration_date == key[: len(self.expiration_date)]:
                put_option = put_exp_map[key]
                break
        for key in call_exp_map.keys():
            if self.expiration_date == key[: len(self.expiration_date)]:
                call_option = call_exp_map[key]
                break
        return put_option, call_option



@dataclass
class OptionLeg:
    symbol: str
    instruction: Instruction
    quantity: int
