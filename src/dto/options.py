from dataclasses import dataclass

from utils.common_utils import OrderType, Instruction


@dataclass
class OptionLeg:
    symbol: str
    instruction: Instruction
    quantity: int
    metadata: dict


@dataclass
class VerticalSpread:
    order_type: OrderType
    quantity: int
    expiration_date: str
    short_leg: OptionLeg
    long_leg: OptionLeg
    price: float
