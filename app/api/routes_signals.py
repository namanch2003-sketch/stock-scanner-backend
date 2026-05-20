from datetime import datetime

from fastapi import APIRouter, Query

from app.schemas.signal_schema import SignalSchema
from app.services import signal_service

router = APIRouter()


@router.get("/signals", response_model=list[SignalSchema])
def get_signals(
    symbol: str | None = Query(default=None),
    timeframe: str | None = Query(default=None),
    signal_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1),
    offset: int | None = Query(default=None, ge=0),
) -> list[SignalSchema]:
    signals = signal_service.get_filtered_signals(
        symbol=symbol,
        timeframe=timeframe,
        signal_type=signal_type,
        status=status,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return [SignalSchema.model_validate(signal) for signal in signals]


@router.get("/signals/grouped", response_model=dict[str, list[SignalSchema]])
def get_grouped_signals() -> dict[str, list[SignalSchema]]:
    grouped = signal_service.get_grouped_signals()
    return {
        timeframe: [SignalSchema.model_validate(signal) for signal in signals]
        for timeframe, signals in grouped.items()
    }
