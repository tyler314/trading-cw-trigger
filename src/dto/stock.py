import logging
import watchtower
import yfinance as yf
import numpy as np

from dto.candle import Candle
from utils.common_utils import transform_ticker, TradingPlatforms

logging.basicConfig(level=logging.ERROR, handlers=[watchtower.CloudWatchLogHandler()])
logger = logging.getLogger(__name__)


class Stock:
    ATR_TIME_FRAME_DAYS = 14

    def __init__(self, ticker):
        self.ticker: str = ticker
        self.candles: list = self._get_candles()
        self.atr: float = self._get_atr()

    def _get_candles(self) -> list:
        candles = np.empty(self.ATR_TIME_FRAME_DAYS, dtype=Candle)
        data = yf.Ticker(transform_ticker(self.ticker, TradingPlatforms.YAHOO)).history(
            period=str(Stock.ATR_TIME_FRAME_DAYS) + "d"
        )
        if len(data) == 0:
            msg = 'yfinance library unable to look up ticker "{}".'.format(self.ticker)
            logging.error(msg)
            raise ValueError(msg)
        for i in range(1, self.ATR_TIME_FRAME_DAYS + 1):
            candles[i - 1] = Candle(
                open=round(data.Open[-i], 2),
                close=round(data.Close[-i], 2),
                high=round(data.High[-i], 2),
                low=round(data.Low[-i], 2),
            )
        return candles

    def _get_atr(self) -> float:
        atr_sum = 0.0
        for candle in self.candles:
            atr_sum += candle.daily_range
        return atr_sum / self.ATR_TIME_FRAME_DAYS
