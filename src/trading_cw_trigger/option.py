from dataclasses import dataclass
from enum import Enum


class OptionAttribute(Enum):
    CREDIT = "NET_CREDIT"
    DEBIT = "NET_DEBIT"
    BUY_TO_OPEN = "BUY_TO_OPEN"
    BUY_TO_CLOSE = "BUY_TO_CLOSE"
    SELL_TO_OPEN = "SELL_TO_OPEN"
    SELL_TO_CLOSE = "SELL_TO_CLOSE"


@dataclass
class Option:
    ticker: str
    instruction: OptionAttribute
    quantity: int


@dataclass
class VerticalSpread:
    long_leg: Option
    short_leg: Option
    order_type: OptionAttribute
    price: float
