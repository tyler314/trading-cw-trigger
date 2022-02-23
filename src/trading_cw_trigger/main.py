import os
import sys

from dto.option import VerticalSpread, OrderType

sys.path.append(os.getcwd())

TICKER = "SPX"


def main():
    return VerticalSpread(TICKER, 1, 0.5, OrderType.CREDIT)

if __name__ == "__main__":
    main()
