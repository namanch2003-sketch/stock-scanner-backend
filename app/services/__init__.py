import os

from app.models.stock import Stock
from app.services.market_data_service import MarketDataService
from app.services.rule_engine import RuleEngine
from app.services.scanner_service import ScannerService
from app.services.signal_service import SignalService
from app.services.watchlist_service import WatchlistService
from app.services.websocket_manager import WebSocketManager

watchlist_service = WatchlistService()
rule_engine = RuleEngine()
signal_service = SignalService()
websocket_manager = WebSocketManager()

import logging as _logging

_logger = _logging.getLogger(__name__)

use_live_data = os.getenv("USE_LIVE_DATA", "false").lower() == "true"

if use_live_data:
    dhan_client_id = os.getenv("DHAN_CLIENT_ID", "")
    dhan_access_token = os.getenv("DHAN_ACCESS_TOKEN", "")
    if not dhan_client_id or not dhan_access_token:
        _logger.warning(
            "USE_LIVE_DATA=true but DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN is missing — "
            "falling back to mock market data."
        )
        use_live_data = False
        market_data_service = MarketDataService(watchlist_service.get_seed_stocks())
    else:
        from app.services.dhan_market_data_service import DhanMarketDataService

        _dhan_stocks = [
            Stock(symbol="PERSISTENT", name="Persistent Systems"),
            Stock(symbol="BSE", name="BSE Ltd"),
            Stock(symbol="DATAPATTNS", name="Data Patterns"),
        ]
        market_data_service = DhanMarketDataService(_dhan_stocks, dhan_client_id, dhan_access_token)
else:
    market_data_service = MarketDataService(watchlist_service.get_seed_stocks())

scanner_service = ScannerService(
    watchlist_service=watchlist_service,
    market_data_service=market_data_service,
    rule_engine=rule_engine,
    signal_service=signal_service,
    websocket_manager=websocket_manager,
    use_live_data=use_live_data,
)
