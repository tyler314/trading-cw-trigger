from dataclasses import dataclass
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


class OrderType(Enum):
    CREDIT = "NET_CREDIT"
    DEBIT = "NET_DEBIT"


class Instruction(Enum):
    BUY_TO_OPEN = "BUY_TO_OPEN"
    SELL_TO_OPEN = "SELL_TO_OPEN"
    BUY_TO_CLOSE = "BUY_TO_CLOSE"
    SELL_TO_CLOSE = "SELL_TO_CLOSE"


class AssetType(Enum):
    OPTION = "OPTION"


class OptionType(Enum):
    CALL = "CALL"
    PUT = "PUT"
    NO_OP = "NO_OP"


@dataclass
class OptionLeg:
    symbol: str
    instruction: Instruction
    quantity: int
    metadata: dict
