import datetime

from dto.stock import Stock
from tda_api.broker import Broker
from utils.common_utils import transform_ticker, TradingPlatforms, OrderType
import logging
import watchtower

logging.basicConfig(level=logging.ERROR, handlers=[watchtower.CloudWatchLogHandler()])
logger = logging.getLogger(__name__)


class VerticalSpread:
    def __init__(
        self,
        ticker: str,
        quantity: int,
        order_type: OrderType,
        expiration_date: datetime,
    ):
        self._broker = Broker()
        self.order_type = order_type
        self.stock = Stock(ticker)
        self.quantity = quantity
        self.expiration_date = expiration_date.strftime("%Y-%m-%d")
        (
            self.put_map,
            self.call_map,
        ) = self._get_put_and_call_maps()  # maps strike-price -> metadata

    def _get_put_and_call_maps(self) -> (dict, dict):
        options = self._broker.option_chain(
            transform_ticker(self.stock.ticker, TradingPlatforms.TDA)
        )
        if options.get("status") == "FAILED":
            msg = "Call to TDA's option chain api failed, with ticker: {}".format(
                self.stock.ticker
            )
            logging.error(msg)
            raise RuntimeError(msg)
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
        if not put_option or not call_option:
            msg = "No options available with an expiration date of {}".format(
                self.expiration_date
            )
            logging.error(msg)
            raise RuntimeError(msg)
        return put_option, call_option
