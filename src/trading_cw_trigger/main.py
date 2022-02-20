from stock import Stock
from option import Option, VerticalSpread, OptionAttribute

TICKER = "SPX"


def main():
    stock = Stock(TICKER)
    if stock.are_consecutive_red_days:
        pass
