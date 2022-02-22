from trading_cw_trigger.dto.stock import Stock
from dto.option import VerticalSpread, OptionAttribute

TICKER = "SPX"


def main():
    stock = Stock(TICKER)
    strategy = VerticalSpread(stock, 1, OptionAttribute.CREDIT)
    strategy.execute_by_strike_price(100)
