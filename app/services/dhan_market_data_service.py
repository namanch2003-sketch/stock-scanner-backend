from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime, timedelta

import httpx

from app.models.candle import Candle
from app.models.stock import Stock

logger = logging.getLogger(__name__)

DHAN_BASE_URL = "https://api.dhan.co/v2"

TIMEFRAME_INTERVAL: dict[str, str] = {"5m": "5", "15m": "15", "1h": "60"}

SECURITY_IDS: dict[str, str] = {
    "PERSISTENT": "11718",
    "BSE": "543272",
    "DATAPATTNS": "543872",
}

MAX_CANDLES = 120


class DhanMarketDataService:
    def __init__(self, stocks: list[Stock], client_id: str, access_token: str) -> None:
        self._stocks = stocks
        self._client_id = client_id
        self._access_token = access_token
        self._candles: dict[tuple[str, str], list[Candle]] = defaultdict(list)

    def _headers(self) -> dict[str, str]:
        return {
            "access-token": self._access_token,
            "client-id": self._client_id,
            "Content-Type": "application/json",
        }

    async def _fetch_candles(
        self,
        client: httpx.AsyncClient,
        symbol: str,
        timeframe: str,
        from_date: str,
        to_date: str,
    ) -> list[Candle]:
        security_id = SECURITY_IDS.get(symbol)
        if not security_id:
            logger.warning("No security ID mapping for symbol %s — skipping", symbol)
            return []

        payload = {
            "securityId": security_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "interval": TIMEFRAME_INTERVAL[timeframe],
            "fromDate": from_date,
            "toDate": to_date,
        }

        try:
            response = await client.post(
                f"{DHAN_BASE_URL}/charts/intraday",
                headers=self._headers(),
                json=payload,
            )
            if response.status_code != 200:
                logger.error(
                    "Dhan API error for %s %s: status=%d body=%s",
                    symbol,
                    timeframe,
                    response.status_code,
                    response.text,
                )
                return []

            data = response.json()

            if not isinstance(data, dict) or "timestamp" not in data:
                logger.error(
                    "Unexpected Dhan response for %s %s — full response: %s",
                    symbol,
                    timeframe,
                    data,
                )
                return []

            timestamps = data.get("timestamp", [])
            opens = data.get("open", [])
            highs = data.get("high", [])
            lows = data.get("low", [])
            closes = data.get("close", [])
            volumes = data.get("volume", [])

            candles: list[Candle] = []
            for i, ts in enumerate(timestamps):
                try:
                    candle = Candle(
                        symbol=symbol,
                        timeframe=timeframe,
                        open=float(opens[i]),
                        high=float(highs[i]),
                        low=float(lows[i]),
                        close=float(closes[i]),
                        volume=int(volumes[i]),
                        candle_time=datetime.fromtimestamp(ts, tz=UTC),
                    )
                    candles.append(candle)
                except (IndexError, ValueError, TypeError) as exc:
                    logger.warning(
                        "Failed to parse candle at index %d for %s %s: %s",
                        i,
                        symbol,
                        timeframe,
                        exc,
                    )

            return candles

        except httpx.RequestError as exc:
            logger.error("HTTP request failed for %s %s: %s", symbol, timeframe, exc)
            return []

    async def bootstrap(self) -> None:
        logger.info("Bootstrapping live Dhan market data...")
        print("Bootstrapping live Dhan market data...")

        today = datetime.now(UTC)
        to_date = today.strftime("%Y-%m-%d")
        # Fetch 7 calendar days back to guarantee 5 trading days
        from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")

        async with httpx.AsyncClient(timeout=30.0) as client:
            for stock in self._stocks:
                for timeframe in TIMEFRAME_INTERVAL:
                    candles = await self._fetch_candles(
                        client, stock.symbol, timeframe, from_date, to_date
                    )
                    if candles:
                        self._candles[(stock.symbol, timeframe)] = candles[-MAX_CANDLES:]
                        count = len(self._candles[(stock.symbol, timeframe)])
                        logger.info("Loaded %d candles for %s %s", count, stock.symbol, timeframe)
                        print(f"Loaded {count} candles for {stock.symbol} {timeframe}")
                    else:
                        logger.warning("No candles loaded for %s %s", stock.symbol, timeframe)
                        print(f"WARNING: No candles loaded for {stock.symbol} {timeframe}")

        logger.info("Bootstrap complete. Starting scanner loop.")
        print("Bootstrap complete. Starting scanner loop.")

    async def refresh(self) -> None:
        today = datetime.now(UTC)
        to_date = today.strftime("%Y-%m-%d")
        from_date = (today - timedelta(days=2)).strftime("%Y-%m-%d")

        async with httpx.AsyncClient(timeout=30.0) as client:
            for stock in self._stocks:
                for timeframe in TIMEFRAME_INTERVAL:
                    candles = await self._fetch_candles(
                        client, stock.symbol, timeframe, from_date, to_date
                    )
                    if not candles:
                        continue

                    existing = self._candles[(stock.symbol, timeframe)]
                    existing_times = {c.candle_time for c in existing}
                    new_candles = [c for c in candles if c.candle_time not in existing_times]

                    if new_candles:
                        existing.extend(new_candles)
                        if len(existing) > MAX_CANDLES:
                            self._candles[(stock.symbol, timeframe)] = existing[-MAX_CANDLES:]
                        logger.debug(
                            "Refreshed %d new candles for %s %s",
                            len(new_candles),
                            stock.symbol,
                            timeframe,
                        )

    def get_candles(self, symbol: str, timeframe: str, limit: int = 50) -> list[Candle]:
        candles = self._candles.get((symbol, timeframe), [])
        return candles[-limit:]

    def get_latest_pair(self, symbol: str, timeframe: str) -> tuple[Candle, Candle] | None:
        candles = self._candles.get((symbol, timeframe), [])
        if len(candles) < 2:
            return None
        return candles[-2], candles[-1]
