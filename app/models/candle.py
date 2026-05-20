from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Candle:
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    candle_time: datetime
