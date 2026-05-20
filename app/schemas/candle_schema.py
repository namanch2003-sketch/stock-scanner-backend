from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandleSchema(BaseModel):
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    candle_time: datetime

    model_config = ConfigDict(from_attributes=True)
