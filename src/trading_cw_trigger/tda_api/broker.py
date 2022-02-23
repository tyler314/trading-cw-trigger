import os
from tda import auth
from lib import config
from dto.strategy import Strategy


class Broker:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        token_path = os.path.join(os.path.dirname(__file__), "../lib", "token.json")
        self.c = auth.client_from_token_file(token_path, config.api_key)

    def quote(self, ticker):
        response = self.c.get_quote(ticker)
        return response.json()

    def option_chain(self, ticker):
        response = self.c.get_option_chain(ticker)
        return response.json()

    def option_order(self):
        order_body = {
            "orderType": self.strategy.order_type,
            "session": "NORMAL",
            "price": self.strategy.price,
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": self.strategy.long_leg.instruction,  # "BUY_TO_OPEN",
                    "quantity": self.strategy.long_leg.quantity,
                    "instrument": {"symbol": self.strategy.long_leg.symbol, "assetType": self.strategy.asset_type},  # "AAPL_022522P115"
                },
                {
                    "instruction": self.strategy.short_leg.instruction,  # "SELL_TO_OPEN",
                    "quantity": self.strategy.short_leg.quantity,
                    "instrument": {"symbol": self.strategy.short_leg.symbol, "assetType": self.strategy.asset_type},  # "AAPL_022522P120"
                },
            ],
        }
        self.c.place_order(config.account_id, order_body)
        return {"code": "ok"}
