import os
import sys

from dto.strategy import Dte1
from utils.common_utils import OrderType

sys.path.append(os.getcwd())

TICKER = "AAPL"


def main(ticker, derp):
    return Dte1(ticker=ticker, order_type=OrderType.CREDIT, buying_power=derp)


if __name__ == "__main__":
    main(TICKER, 1)
