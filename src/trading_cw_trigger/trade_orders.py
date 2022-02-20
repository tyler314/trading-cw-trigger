import os

from tda import auth

from lib import config

token_path = os.path.join(os.path.dirname(__file__), "lib", "token.json")
c = auth.client_from_token_file(token_path, config.api_key)


def quote(ticker):
    response = c.get_quote(ticker)
    return response.json()


def option_chain(ticker):
    response = c.get_option_chain(ticker)
    return response.json()


def option_order():
    order_body = {
        "orderType": "NET_CREDIT",
        "session": "NORMAL",
        "price": "1.50",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
                "instruction": "BUY_TO_OPEN",
                "quantity": 1,
                "instrument": {"symbol": "AAPL_022522P115", "assetType": "OPTION"},
            },
            {
                "instruction": "SELL_TO_OPEN",
                "quantity": 1,
                "instrument": {"symbol": "AAPL_022522P120", "assetType": "OPTION"},
            },
        ],
    }
    c.place_order(config.account_id, order_body)
    return {"code": "ok"}
