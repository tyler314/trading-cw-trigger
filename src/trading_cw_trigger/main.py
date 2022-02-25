import os
import sys

from dto.strategy import Dte1
from utils.common_utils import OrderType

sys.path.append(os.getcwd())

TICKER = "AAPL"


def main(ticker):
    return Dte1(ticker, 1, OrderType.CREDIT)


if __name__ == "__main__":
    main(TICKER)
