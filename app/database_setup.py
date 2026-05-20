from __future__ import annotations

from app.db import Base, SessionLocal, engine
from app.db_models import ChartinkAlert, SignalRecord, StockRecord  # noqa: F401
from app.models.stock import Stock


DEFAULT_STOCKS: tuple[Stock, ...] = (
    Stock(symbol="RELIANCE", name="Reliance Industries"),
    Stock(symbol="TCS", name="Tata Consultancy Services"),
    Stock(symbol="INFY", name="Infosys"),
    Stock(symbol="HDFCBANK", name="HDFC Bank"),
    Stock(symbol="ICICIBANK", name="ICICI Bank"),
    Stock(symbol="SBIN", name="State Bank of India"),
    Stock(symbol="AXISBANK", name="Axis Bank"),
    Stock(symbol="LT", name="Larsen & Toubro"),
    Stock(symbol="ITC", name="ITC"),
    Stock(symbol="KOTAKBANK", name="Kotak Mahindra Bank"),
    Stock(symbol="BAJFINANCE", name="Bajaj Finance"),
    Stock(symbol="HINDUNILVR", name="Hindustan Unilever"),
    Stock(symbol="MARUTI", name="Maruti Suzuki"),
    Stock(symbol="SUNPHARMA", name="Sun Pharmaceutical"),
    Stock(symbol="BHARTIARTL", name="Bharti Airtel"),
    Stock(symbol="WIPRO", name="Wipro"),
    Stock(symbol="HCLTECH", name="HCL Technologies"),
    Stock(symbol="ULTRACEMCO", name="UltraTech Cement"),
    Stock(symbol="ASIANPAINT", name="Asian Paints"),
    Stock(symbol="TITAN", name="Titan Company"),
    Stock(symbol="ADANIENT", name="Adani Enterprises"),
    Stock(symbol="ADANIPORTS", name="Adani Ports"),
    Stock(symbol="NTPC", name="NTPC"),
    Stock(symbol="POWERGRID", name="Power Grid Corporation"),
    Stock(symbol="ONGC", name="Oil and Natural Gas Corporation"),
    Stock(symbol="COALINDIA", name="Coal India"),
    Stock(symbol="TATAMOTORS", name="Tata Motors"),
    Stock(symbol="TATASTEEL", name="Tata Steel"),
    Stock(symbol="JSWSTEEL", name="JSW Steel"),
    Stock(symbol="INDUSINDBK", name="IndusInd Bank"),
    Stock(symbol="BAJAJFINSV", name="Bajaj Finserv"),
    Stock(symbol="NESTLEIND", name="Nestle India"),
    Stock(symbol="M&M", name="Mahindra & Mahindra"),
    Stock(symbol="TECHM", name="Tech Mahindra"),
    Stock(symbol="DRREDDY", name="Dr Reddy's Laboratories"),
    Stock(symbol="CIPLA", name="Cipla"),
    Stock(symbol="GRASIM", name="Grasim Industries"),
    Stock(symbol="HEROMOTOCO", name="Hero MotoCorp"),
    Stock(symbol="EICHERMOT", name="Eicher Motors"),
    Stock(symbol="HDFCLIFE", name="HDFC Life Insurance"),
)


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    seed_stocks_if_empty()


def seed_stocks_if_empty() -> None:
    with SessionLocal() as session:
        has_stock = session.query(StockRecord.id).first()
        if has_stock:
            return

        session.add_all(
            [
                StockRecord(
                    symbol=stock.symbol,
                    name=stock.name,
                    exchange=stock.exchange,
                    is_active=stock.is_active,
                )
                for stock in DEFAULT_STOCKS
            ]
        )
        session.commit()


def clear_database() -> None:
    with SessionLocal() as session:
        session.query(SignalRecord).delete()
        session.query(StockRecord).delete()
        session.commit()
