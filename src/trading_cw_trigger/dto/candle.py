from dataclasses import dataclass


@dataclass
class Candle:
    open: float
    close: float
    high: float
    low: float

    @property
    def daily_range(self) -> float:
        return round(self.high - self.low, 2)
