from pydantic import BaseModel, ConfigDict


class StockSchema(BaseModel):
    symbol: str
    name: str
    exchange: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
