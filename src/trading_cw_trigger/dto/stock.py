import os
from tda import auth
from src.trading_cw_trigger.lib import config
import yfinance as yf
import json
from candle import Candle
from src.trading_cw_trigger.utils.common_utils import std_to_tda, std_to_yf

token_path = os.path.join(os.path.dirname(__file__), "../lib", "token.json")
c = auth.client_from_token_file(token_path, config.api_key)
ATR_TIME_FRAME = 14


class Stock:
    def __init__(self, ticker):
        self.ticker: str = ticker
        self.candles: list = []
        self.atr: float = 0.0
        self.most_recent_price: float = 0
        self._calculate_data()

    def _calculate_data(self):
        raw_data = yf.download(
            self.ticker
            if self.ticker not in std_to_yf.keys()
            else std_to_yf[self.ticker],
            start="2022-01-01",
        ).values
        for i in range(1, 15):
            candle = raw_data[-i]
            self.candles.append(
                Candle(
                    open=round(candle[0], 2),
                    high=round(candle[1], 2),
                    low=round(candle[2], 2),
                    close=round(candle[3], 2),
                )
            )
        last_quote_str = (
            "{"
            + c.get_price_history(
                self.ticker
                if self.ticker not in std_to_tda
                else std_to_tda[self.ticker]
            )
            .text.split("},{")[-1]
            .split("}]")[0]
            + "}"
        )
        last_quote = json.loads(last_quote_str)
        self.candles[0].close = last_quote["close"]
        for candle in self.candles:
            self.atr += candle.daily_range
        self.atr /= ATR_TIME_FRAME
