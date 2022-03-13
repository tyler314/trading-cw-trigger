import os
import tempfile
import shutil
from tda import auth
from lib import config
from utils.common_utils import OrderType, AssetType
from dto.options import OptionLeg


class Broker:
    def __init__(self):
        token_path = os.path.join(
            os.path.dirname(__file__), "../lib", "auth_token.json"
        )
        self._tmp_dir = tempfile.mkdtemp(prefix="/tmp/")
        shutil.copy2(token_path, self._tmp_dir)
        self.client = auth.client_from_token_file(
            os.path.join(self._tmp_dir, "auth_token.json"), config.api_key
        )

    def __del__(self):
        shutil.rmtree(self._tmp_dir)

    def quote(self, ticker):
        response = self.client.get_quote(ticker)
        return response.json()

    def option_chain(self, ticker):
        response = self.client.get_option_chain(ticker)
        return response.json()

    def place_option_spread_order(
        self,
        order_type: OrderType,
        price: float,
        asset_type: AssetType,
        long_leg: OptionLeg,
        short_leg: OptionLeg,
    ):
        order_body = {
            "orderType": order_type.value,
            "session": "NORMAL",
            "price": str(price) + "0",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": long_leg.instruction.value,
                    "quantity": long_leg.quantity,
                    "instrument": {
                        "symbol": long_leg.symbol,
                        "assetType": asset_type.value,
                    },
                },
                {
                    "instruction": short_leg.instruction.value,
                    "quantity": short_leg.quantity,
                    "instrument": {
                        "symbol": short_leg.symbol,
                        "assetType": asset_type.value,
                    },
                },
            ],
        }
        self.client.place_order(config.account_id, order_body)
        return {"code": "ok", "order_body": str(order_body)}
