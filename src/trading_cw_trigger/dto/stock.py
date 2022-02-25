import os
from tda import auth
from lib import config
import yfinance as yf
import datetime
from dto.candle import Candle
from utils.common_utils import std_to_yf

token_path = os.path.join(os.path.dirname(__file__), "../lib", "token.json")
c = auth.client_from_token_file(token_path, config.api_key)


class Stock:
    ATR_TIME_FRAME = 14

    def __init__(self, ticker):
        self.ticker: str = ticker
        self.candles: list = self._get_candles()
        self.atr: float = self._get_atr()

    def _get_candles(self) -> list:
        candles = []
        one_month_ago = datetime.date.today() - datetime.timedelta(hours=24 * 30)
        raw_data = yf.download(
            self.ticker
            if self.ticker not in std_to_yf.keys()
            else std_to_yf[self.ticker],
            start=one_month_ago.strftime("%Y-%m-%d"),
        ).values
        for i in range(1, 15):
            candle = raw_data[-i]
            candles.append(
                Candle(
                    open=round(candle[0], 2),
                    high=round(candle[1], 2),
                    low=round(candle[2], 2),
                    close=round(candle[3], 2),
                )
            )
        return candles

    def _get_atr(self) -> float:
        atr_sum = 0.0
        for candle in self.candles:
            atr_sum += candle.daily_range
        return atr_sum / self.ATR_TIME_FRAME
