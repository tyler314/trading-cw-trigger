import unittest
import random
from dto.candle import Candle


class TestCandle(unittest.TestCase):
    def test_daily_range(self):
        multiplier = 100
        for i in range(10):
            open_price = random.random() * multiplier
            close_close = random.random() * multiplier
            candle = Candle(
                open=open_price,
                close=close_close,
                high=max(open_price, close_close),
                low=min(open_price, close_close),
            )
            self.assertEqual(
                candle.daily_range, round(abs(candle.high - candle.low), 2)
            )


if __name__ == "__main__":
    unittest.main()
