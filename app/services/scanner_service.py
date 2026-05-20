from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from app.config import settings
from app.models.signal import Signal
from app.schemas.signal_schema import SignalSchema
from app.services.market_data_service import MarketDataService
from app.services.rule_engine import RuleEngine
from app.services.signal_service import SignalService
from app.services.watchlist_service import WatchlistService
from app.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


class ScannerService:
    def __init__(
        self,
        watchlist_service: WatchlistService,
        market_data_service: MarketDataService,
        rule_engine: RuleEngine,
        signal_service: SignalService,
        websocket_manager: WebSocketManager,
        use_live_data: bool = False,
    ) -> None:
        self.watchlist_service = watchlist_service
        self.market_data_service = market_data_service
        self.rule_engine = rule_engine
        self.signal_service = signal_service
        self.websocket_manager = websocket_manager
        self._use_live_data = use_live_data
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._running = True
        if self._use_live_data:
            await self.market_data_service.bootstrap()
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run_loop(self) -> None:
        while self._running:
            await self.scan_once()
            await asyncio.sleep(settings.scan_interval_seconds)

    async def scan_once(self) -> None:
        logger.info("Scan started")
        print("scan started")

        if self._use_live_data:
            await self.market_data_service.refresh()
        else:
            self.market_data_service.advance_market()

        new_signals: list[Signal] = []

        for stock in self.watchlist_service.get_active_stocks():
            for timeframe in settings.timeframes:
                pair = self.market_data_service.get_latest_pair(stock.symbol, timeframe)
                if not pair:
                    continue
                # The market data service advances full candles, so this pair represents
                # the previous completed candle and the latest completed candle.
                previous, current = pair
                signal = self.rule_engine.evaluate(previous, current)
                if signal and self.signal_service.add_signal(signal):
                    new_signals.append(signal)

        for signal in new_signals:
            await self.websocket_manager.broadcast_json(
                {
                    "event": "signal.created",
                    "signal": SignalSchema.model_validate(signal).model_dump(mode="json"),
                }
            )

        logger.info("[SCAN] %d new signals", len(new_signals))
        print("scan completed")
        print(f"[SCAN] {len(new_signals)} new signals")
