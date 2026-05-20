from fastapi import APIRouter

from app.schemas.stock_schema import StockSchema
from app.services import watchlist_service

router = APIRouter()


@router.get("/watchlist", response_model=list[StockSchema])
def get_watchlist() -> list[StockSchema]:
    return [StockSchema.model_validate(stock) for stock in watchlist_service.get_watchlist()]
