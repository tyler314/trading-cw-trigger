from dataclasses import dataclass


@dataclass
class Candle:
    open: float
    close: float
    high: float
    low: float

    @property
    def daily_range(self) -> float:
        return self.high - self.low
