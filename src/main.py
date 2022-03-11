import os
import sys

from strategies.dte1_ic import Dte1IC
from strategies.dte1 import Dte1
from utils.common_utils import OrderType
import time

sys.path.append(os.getcwd())

TICKER = "AAPL"


def get_dte1(ticker, derp):
    return Dte1(ticker=ticker, order_type=OrderType.CREDIT, buying_power=derp)


def get_ic(ticker, derp):
    return Dte1IC(ticker=ticker, order_type=OrderType.CREDIT, buying_power=derp)


def main():
    t = time.time()
    xx = get_dte1(TICKER, 500)
    xx.execute()
    print("Elapsed time: ", time.time() - t)


if __name__ == "__main__":
    x = get_dte1(TICKER, 1)
    x.execute()
