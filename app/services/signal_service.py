from __future__ import annotations

from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.db_models import SignalRecord
from app.models.signal import Signal


class SignalService:
    def add_signal(self, signal: Signal) -> bool:
        with SessionLocal() as session:
            record = SignalRecord(
                id=signal.id,
                symbol=signal.symbol,
                timeframe=signal.timeframe,
                signal_type=signal.signal_type,
                trigger_price=signal.trigger_price,
                current_price=signal.current_price,
                rule_name=signal.rule_name,
                rule_description=signal.rule_description,
                conditions_met=signal.conditions_met,
                candle_time=signal.candle_time,
                triggered_at=signal.triggered_at,
                status=signal.status,
                unique_key=signal.id,
                previous_high=signal.previous_high,
                previous_low=signal.previous_low,
                current_high=signal.current_high,
                current_low=signal.current_low,
                current_close=signal.current_close,
            )
            session.add(record)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return False
        return True

    def get_all_signals(self) -> list[SignalRecord]:
        with SessionLocal() as session:
            return (
                session.query(SignalRecord)
                .order_by(SignalRecord.triggered_at.desc())
                .all()
            )

    def get_filtered_signals(
        self,
        symbol: str | None = None,
        timeframe: str | None = None,
        signal_type: str | None = None,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SignalRecord]:
        with SessionLocal() as session:
            query = session.query(SignalRecord)

            if symbol:
                normalized_symbol = f"%{symbol.strip().upper()}%"
                query = query.filter(SignalRecord.symbol.ilike(normalized_symbol))

            if timeframe:
                query = query.filter(SignalRecord.timeframe == timeframe)

            if signal_type:
                query = query.filter(SignalRecord.signal_type == signal_type)

            if status:
                query = query.filter(SignalRecord.status == status)

            if from_date:
                query = query.filter(SignalRecord.triggered_at >= from_date)

            if to_date:
                query = query.filter(SignalRecord.triggered_at <= to_date)

            query = query.order_by(SignalRecord.triggered_at.desc())

            if offset:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            return query.all()

    def get_grouped_signals(self) -> dict[str, list[SignalRecord]]:
        grouped: dict[str, list[SignalRecord]] = {"5m": [], "15m": [], "1h": []}
        for signal in self.get_all_signals():
            grouped.setdefault(signal.timeframe, []).append(signal)
        return grouped

    def clear_signals(self) -> None:
        with SessionLocal() as session:
            session.query(SignalRecord).delete()
            session.commit()
