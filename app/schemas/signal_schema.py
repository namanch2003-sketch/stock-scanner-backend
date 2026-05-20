from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SignalSchema(BaseModel):
    id: str
    symbol: str
    timeframe: str
    signal_type: str
    trigger_price: float
    current_price: float
    rule_name: str
    triggered_at: datetime
    candle_time: datetime
    previous_high: float
    previous_low: float
    current_high: float
    current_low: float
    current_close: float
    rule_description: str
    conditions_met: list[str]
    status: str

    model_config = ConfigDict(from_attributes=True)
