from dataclasses import dataclass


@dataclass(slots=True)
class Stock:
    symbol: str
    name: str
    exchange: str = "NSE"
    is_active: bool = True
