import os
from tda import auth
from lib import config
from utils.common_utils import OrderType, AssetType, OptionLeg

token_path = os.path.join(os.path.dirname(__file__), "../lib", "token.json")
c = auth.client_from_token_file(token_path, config.api_key)


def quote(ticker):
    response = c.get_quote(ticker)
    return response.json()


def option_chain(ticker):
    response = c.get_option_chain(ticker)
    return response.json()


def place_option_spread_order(
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
    c.place_order(config.account_id, order_body)
    return {"code": "ok", "order_body": str(order_body)}

