import os
import unittest
import datetime
import json
from unittest.mock import MagicMock, patch
from utils.common_utils import OrderType, OptionType
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
        short_leg_metadata = self.option_factory.call_map["4200.0"]
        long_leg_metadata = self.option_factory.call_map["4250.0"]
