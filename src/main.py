import os
import sys

from dto.strategy import Dte1, DteIC1
from utils.common_utils import OrderType

sys.path.append(os.getcwd())

TICKER = "AAPL"


def get_dte1(ticker, derp):
    return Dte1(ticker=ticker, order_type=OrderType.CREDIT, buying_power=derp)


def get_ic(ticker, derp):
    return DteIC1(ticker=ticker, order_type=OrderType.CREDIT, buying_power=derp)


if __name__ == "__main__":
    x = get_dte1(TICKER, 1)
    x.execute()
