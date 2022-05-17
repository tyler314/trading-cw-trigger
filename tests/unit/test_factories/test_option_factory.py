import os
import unittest
import datetime
import json
from unittest.mock import MagicMock, patch
from utils.common_utils import OrderType, OptionType, Instruction
from dto.options import OptionLeg, VerticalSpread
from factories.option_factory import OptionFactory


TICKER = "SPX"
ORDER_TYPE = OrderType.CREDIT
EXPIRATION = datetime.datetime(2022, 4, 25, 11, 37, 45, 309012)
QUANTITY = 1
PRICE = 0.50


def _get_put_map():
    with open(
        os.path.join(os.path.dirname(__file__), "../common/test_put_map.json"), "r"
    ) as put_map_file:
        return json.load(put_map_file)


def _get_call_map():
    with open(
        os.path.join(os.path.dirname(__file__), "../common/test_call_map.json"), "r"
    ) as call_map_file:
        return json.load(call_map_file)


def get_leg(strike: str, option_type: OptionType, instruction: Instruction):
    if option_type == OptionType.CALL:
        option_map = _get_call_map()
    else:
        option_map = _get_put_map()
    return OptionLeg(
        instruction=instruction,
        quantity=1,
        symbol=option_map[strike][0]["symbol"],
        metadata=option_map[strike][0],
    )


class TestOptionFactory(unittest.TestCase):
    @patch.multiple(
        "factories.option_factory.OptionFactory",
        _get_put_and_call_maps=MagicMock(
            return_value=(_get_put_map(), _get_call_map())
        ),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.option_factory = OptionFactory(TICKER, QUANTITY, ORDER_TYPE, EXPIRATION)

    def test_get_legs_for_vertical_spread(self):
        rough_strike = 4101.1234
        width = 500
        # Test Put
        option_type = OptionType.PUT
        short_leg, long_leg = self.option_factory._get_legs_for_vertical_spread(
            rough_strike, width, option_type
        )
        self.assertEqual(short_leg.metadata["symbol"][-4:], "4100")
        self.assertEqual(long_leg.metadata["symbol"][-4:], str(4100 - width // 100))
        # Test Call
        option_type = OptionType.CALL
        short_leg, long_leg = self.option_factory._get_legs_for_vertical_spread(
            rough_strike, width, option_type
        )
        self.assertEqual(short_leg.metadata["symbol"][-4:], "4100")
        self.assertEqual(long_leg.metadata["symbol"][-4:], str(4100 + width // 100))

    def test_calculate_price_for_vertical_spread(self):
        # Calls
        short_leg = get_leg("4200.0", OptionType.CALL, Instruction.SELL_TO_OPEN)
        long_leg = get_leg("4250.0", OptionType.CALL, Instruction.SELL_TO_OPEN)
        self.assertEqual(
            29.4,
            self.option_factory._calculate_price_for_vertical_spread(
                OptionType.CALL, short_leg, long_leg
            ),
        )
        short_leg = get_leg("4000.0", OptionType.CALL, Instruction.SELL_TO_OPEN)
        long_leg = get_leg("4100.0", OptionType.CALL, Instruction.SELL_TO_OPEN)
        self.assertEqual(
            99.45,
            self.option_factory._calculate_price_for_vertical_spread(
                OptionType.CALL, short_leg, long_leg
            ),
        )
        # Puts
        short_leg = get_leg("4200.0", OptionType.PUT, Instruction.SELL_TO_OPEN)
        long_leg = get_leg("4150.0", OptionType.PUT, Instruction.SELL_TO_OPEN)
        self.assertEqual(
            6.5,
            self.option_factory._calculate_price_for_vertical_spread(
                OptionType.CALL, short_leg, long_leg
            ),
        )
        short_leg = get_leg("4100.0", OptionType.PUT, Instruction.SELL_TO_OPEN)
        long_leg = get_leg("4000.0", OptionType.PUT, Instruction.SELL_TO_OPEN)
        self.assertEqual(
            0.2,
            self.option_factory._calculate_price_for_vertical_spread(
                OptionType.CALL, short_leg, long_leg
            ),
        )

    def test_get_vertical_spread(self):
        actual_vertical_spread = self.option_factory.get_vertical_spread(
            short_leg_strike=4000, buying_power=1000, option_type=OptionType.CALL
        )
        expected_vertical_spread = VerticalSpread(
            order_type=OrderType.CREDIT,
            quantity=1,
            expiration_date=EXPIRATION.strftime("%Y-%m-%d"),
            short_leg=get_leg("4000.0", OptionType.CALL, Instruction.SELL_TO_OPEN),
            long_leg=get_leg("4010.0", OptionType.CALL, Instruction.BUY_TO_OPEN),
            price=9.6,
        )
        self.assertEqual(actual_vertical_spread, expected_vertical_spread)

        actual_vertical_spread = self.option_factory.get_vertical_spread(
            short_leg_strike=4200, buying_power=500, option_type=OptionType.PUT
        )
        expected_vertical_spread = VerticalSpread(
            order_type=OrderType.CREDIT,
            quantity=1,
            expiration_date=EXPIRATION.strftime("%Y-%m-%d"),
            short_leg=get_leg("4200.0", OptionType.PUT, Instruction.SELL_TO_OPEN),
            long_leg=get_leg("4195.0", OptionType.PUT, Instruction.BUY_TO_OPEN),
            price=1.15,
        )
        self.assertEqual(actual_vertical_spread, expected_vertical_spread)
