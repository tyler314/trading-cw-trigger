from enum import Enum

std_to_tda = {"SPX": "$SPX.X", "NDX": "$NDX.X"}

std_to_yf = {"SPX": "^GSPC"}


class TradingPlatforms(Enum):
    YAHOO = "YAHOO_FINANCE"
    TDA = "TD_AMERITRADE"


def transform_ticker(ticker, tp: TradingPlatforms):
    if tp == TradingPlatforms.YAHOO:
        return ticker if ticker not in std_to_tda.keys() else std_to_tda[ticker]
    elif tp == TradingPlatforms.TDA:
        return ticker if ticker not in std_to_tda.keys() else std_to_tda[ticker]
    return ticker
