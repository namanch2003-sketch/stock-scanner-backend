from app.database_setup import DEFAULT_STOCKS
from app.db import SessionLocal
from app.db_models import StockRecord


class WatchlistService:
    def get_seed_stocks(self):
        return list(DEFAULT_STOCKS)

    def get_watchlist(self) -> list[StockRecord]:
        with SessionLocal() as session:
            return session.query(StockRecord).order_by(StockRecord.symbol.asc()).all()

    def get_active_stocks(self) -> list[StockRecord]:
        with SessionLocal() as session:
            return (
                session.query(StockRecord)
                .filter(StockRecord.is_active.is_(True))
                .order_by(StockRecord.symbol.asc())
                .all()
            )
