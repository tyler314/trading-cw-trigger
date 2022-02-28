import os

import logging
import watchtower
import yfinance as yf
from tda import auth

from dto.candle import Candle
from lib import config
from utils.common_utils import transform_ticker, TradingPlatforms

token_path = os.path.join(os.path.dirname(__file__), "../lib", "token.json")
c = auth.client_from_token_file(token_path, config.api_key)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())


class Stock:
    ATR_TIME_FRAME_DAYS = 14

    def __init__(self, ticker):
        self.ticker: str = ticker
        self.candles: list = self._get_candles()
        self.atr: float = self._get_atr()

    def _get_candles(self) -> list:
        candles = []
        data = yf.Ticker(transform_ticker(self.ticker, TradingPlatforms.YAHOO)).history(
            period=str(Stock.ATR_TIME_FRAME_DAYS) + "d"
        )
        if len(data) == 0:
            msg = "yfinance library unable to look up ticker \"{}\".".format(self.ticker)
            logging.error(msg)
            raise ValueError(msg)
        for i in range(1, self.ATR_TIME_FRAME_DAYS + 1):
            candles.append(
                Candle(
                    open=round(data.Open[-i], 2),
                    close=round(data.Close[-i], 2),
                    high=round(data.High[-i], 2),
                    low=round(data.Low[-i], 2),
                )
            )
        return candles

    def _get_atr(self) -> float:
        atr_sum = 0.0
        for candle in self.candles:
            atr_sum += candle.daily_range
        return atr_sum / self.ATR_TIME_FRAME_DAYS
