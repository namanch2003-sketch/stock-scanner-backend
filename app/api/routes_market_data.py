from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.schemas.candle_schema import CandleSchema
from app.services import market_data_service

router = APIRouter()


@router.get("/market-data/candles/{symbol}", response_model=list[CandleSchema])
def get_candles(
    symbol: str,
    timeframe: str = Query(default="5m"),
) -> list[CandleSchema]:
    if timeframe not in settings.timeframes:
        raise HTTPException(status_code=400, detail="Unsupported timeframe")

    candles = market_data_service.get_candles(symbol=symbol.upper(), timeframe=timeframe)
    if not candles:
        raise HTTPException(status_code=404, detail="Symbol not found")

    return [CandleSchema.model_validate(candle) for candle in candles]
