import datetime
from enum import Enum
from src.trading_cw_trigger.utils.common_utils import transform_ticker, TradingPlatforms
from trading_cw_trigger.tda_api.trade_orders import option_chain
from src.trading_cw_trigger.dto.stock import Stock

CONSECUTIVE_DAYS = 3


class OptionAttribute(Enum):
    CREDIT = "NET_CREDIT"
    DEBIT = "NET_DEBIT"
    BUY_TO_OPEN = "BUY_TO_OPEN"
    BUY_TO_CLOSE = "BUY_TO_CLOSE"
    SELL_TO_OPEN = "SELL_TO_OPEN"
    SELL_TO_CLOSE = "SELL_TO_CLOSE"


class VerticalSpread:
    def __init__(
        self,
        stock: Stock,
        quantity: int,
        order_type: OptionAttribute,
        expiration_date: datetime.date = None,
        dte: int = 1,
    ):
        self.order_type = order_type
        self.dte = dte
        self.stock = stock
        self.quantity = quantity
        if expiration_date is None:
            self.expiration_date = self._get_expiration_date()
        else:
            self.expiration_date = expiration_date.strftime("%Y-%m-%d")
        (
            self.put_map,
            self.call_map,
        ) = self._get_put_and_call_maps()  # maps strike-price -> metadata

    def _are_consecutive_red_days(self):
        for i in range(CONSECUTIVE_DAYS):
            if self.stock.candles[i].close >= self.stock.candles[i].open:
                return False
        return True

    def _are_consecutive_green_days(self):
        for i in range(CONSECUTIVE_DAYS):
            if self.stock.candles[i].open >= self.stock.candles[i].close:
                return False
        return True

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

    def execute_by_strike_price(self, strike: str):
        pass
