import unittest
from dto.options import VerticalSpread


class TestVerticalSpread(unittest.TestCase):
    TICKER = "AAPL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vs = VerticalSpread()
        pass


if __name__ == "__main__":
    unittest.main()
