from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ChartinkAlert(Base):
    __tablename__ = "chartink_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), index=True)
    trigger_price: Mapped[float] = mapped_column(Float)
    scan_name: Mapped[str] = mapped_column(String(255))
    triggered_at: Mapped[str] = mapped_column(String(20))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ltp: Mapped[float | None] = mapped_column(Float, nullable=True)


class StockRecord(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    exchange: Mapped[str] = mapped_column(String(20), default="NSE")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SignalRecord(Base):
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint("unique_key", name="uq_signals_unique_key"),)

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), index=True)
    timeframe: Mapped[str] = mapped_column(String(10), index=True)
    signal_type: Mapped[str] = mapped_column(String(20), index=True)
    trigger_price: Mapped[float] = mapped_column(Float)
    current_price: Mapped[float] = mapped_column(Float)
    rule_name: Mapped[str] = mapped_column(String(255), index=True)
    rule_description: Mapped[str] = mapped_column(String(1000))
    conditions_met: Mapped[list[str]] = mapped_column(JSON)
    candle_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(50))
    unique_key: Mapped[str] = mapped_column(String(255), nullable=False)
    previous_high: Mapped[float] = mapped_column(Float)
    previous_low: Mapped[float] = mapped_column(Float)
    current_high: Mapped[float] = mapped_column(Float)
    current_low: Mapped[float] = mapped_column(Float)
    current_close: Mapped[float] = mapped_column(Float)
