import unittest
from factories.option_factory import OptionFactory


class TestVerticalSpread(unittest.TestCase):
    TICKER = "AAPL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vs = OptionFactory()
        pass


if __name__ == "__main__":
    unittest.main()
