import unittest
from dto.stock import Stock
from utils.common_utils import transform_ticker, TradingPlatforms
import yfinance as yf


class TestStock(unittest.TestCase):
    TICKER = "SPX"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = yf.Ticker(
            transform_ticker(self.TICKER, TradingPlatforms.YAHOO)
        ).history(period=str(Stock.ATR_TIME_FRAME_DAYS) + "d")
        self.stock = Stock(transform_ticker(self.TICKER, TradingPlatforms.YAHOO))

    def test_open_values(self):
        for i in range(1, Stock.ATR_TIME_FRAME_DAYS + 1):
            self.assertEqual(
                self.stock.candles[i - 1].open, round(self.data.Open[-i], 2)
            )

    def test_close_values(self):
        for i in range(1, Stock.ATR_TIME_FRAME_DAYS + 1):
            self.assertEqual(
                self.stock.candles[i - 1].close, round(self.data.Close[-i], 2)
            )

    def test_high_values(self):
        for i in range(1, Stock.ATR_TIME_FRAME_DAYS + 1):
            self.assertEqual(
                self.stock.candles[i - 1].high, round(self.data.High[-i], 2)
            )

    def test_low_values(self):
        for i in range(1, Stock.ATR_TIME_FRAME_DAYS + 1):
            self.assertEqual(self.stock.candles[i - 1].low, round(self.data.Low[-i], 2))

    def test_atr_values(self):
        atr_expected_value = 0
        for candle in self.stock.candles:
            atr_expected_value += candle.daily_range
        atr_expected_value /= Stock.ATR_TIME_FRAME_DAYS
        for i in range(1, Stock.ATR_TIME_FRAME_DAYS + 1):
            self.assertEqual(self.stock.atr, atr_expected_value)


if __name__ == "__main__":
    unittest.main()
