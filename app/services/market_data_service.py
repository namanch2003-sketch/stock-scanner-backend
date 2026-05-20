from __future__ import annotations

import random
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from app.models.candle import Candle
from app.models.stock import Stock


TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
BASE_PRICES = {
    "RELIANCE": 2850,
    "TCS": 3920,
    "INFY": 1480,
    "HDFCBANK": 1675,
    "ICICIBANK": 1195,
    "SBIN": 845,
    "AXISBANK": 1115,
    "LT": 3725,
    "ITC": 435,
    "KOTAKBANK": 1765,
    "BAJFINANCE": 7060,
    "HINDUNILVR": 2465,
    "MARUTI": 12650,
    "SUNPHARMA": 1740,
    "BHARTIARTL": 1490,
    "WIPRO": 495,
    "HCLTECH": 1610,
    "ULTRACEMCO": 10820,
    "ASIANPAINT": 2920,
    "TITAN": 3560,
}


class MarketDataService:
    def __init__(self, stocks: list[Stock]) -> None:
        self._stocks = stocks
        self._rand = random.Random(42)
        self._candles: dict[tuple[str, str], list[Candle]] = defaultdict(list)
        self._step = 0
        self._bootstrap()

    def _bootstrap(self) -> None:
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        for stock in self._stocks:
            base_price = BASE_PRICES.get(stock.symbol, self._rand.uniform(200, 5000))
            for timeframe, minutes in TIMEFRAME_MINUTES.items():
                candles: list[Candle] = []
                candle_time = now - timedelta(minutes=minutes * 40)
                price = base_price
                for _ in range(40):
                    candle = self._build_neutral_candle(stock.symbol, timeframe, candle_time, price)
                    candles.append(candle)
                    candle_time += timedelta(minutes=minutes)
                    price = candle.close
                self._candles[(stock.symbol, timeframe)] = candles

    def _build_neutral_candle(
        self,
        symbol: str,
        timeframe: str,
        candle_time: datetime,
        anchor_price: float,
    ) -> Candle:
        drift = anchor_price * self._rand.uniform(-0.004, 0.004)
        open_price = anchor_price + drift
        high = open_price * (1 + self._rand.uniform(0.0008, 0.006))
        low = open_price * (1 - self._rand.uniform(0.0008, 0.006))
        close = self._rand.uniform(low, high)
        volume = int(self._rand.uniform(100_000, 2_500_000))
        return Candle(
            symbol=symbol,
            timeframe=timeframe,
            open=round(open_price, 2),
            high=round(max(high, open_price, close), 2),
            low=round(min(low, open_price, close), 2),
            close=round(close, 2),
            volume=volume,
            candle_time=candle_time,
        )

    def _build_buy_candle(self, previous: Candle, candle_time: datetime) -> Candle:
        gap = max(previous.close * 0.0018, 0.5)
        low = max(previous.low + gap, previous.close * 0.998)
        high = max(previous.high + gap * 2.8, low + gap * 2.2)
        close = max(previous.high + gap * 1.6, high - gap * 0.35)
        open_price = max(low + gap * 0.2, previous.close + gap * 0.4)
        return Candle(
            symbol=previous.symbol,
            timeframe=previous.timeframe,
            open=round(min(open_price, high), 2),
            high=round(high, 2),
            low=round(low, 2),
            close=round(min(close, high), 2),
            volume=int(self._rand.uniform(250_000, 3_200_000)),
            candle_time=candle_time,
        )

    def _build_sell_candle(self, previous: Candle, candle_time: datetime) -> Candle:
        gap = max(previous.close * 0.0018, 0.5)
        high = min(previous.high - gap, previous.close * 1.002)
        close = min(previous.low - gap * 1.4, high - gap * 0.6)
        low = min(close - gap * 0.35, previous.low - gap * 2.2)
        open_price = min(high - gap * 0.2, previous.close - gap * 0.3)
        return Candle(
            symbol=previous.symbol,
            timeframe=previous.timeframe,
            open=round(max(open_price, low), 2),
            high=round(max(high, open_price, close), 2),
            low=round(low, 2),
            close=round(close, 2),
            volume=int(self._rand.uniform(250_000, 3_200_000)),
            candle_time=candle_time,
        )

    def _build_next_candle(self, previous: Candle, candle_time: datetime) -> Candle:
        selector = (self._step + len(previous.symbol) + len(previous.timeframe)) % 11
        if selector in {0, 5}:
            return self._build_buy_candle(previous, candle_time)
        if selector in {3, 8}:
            return self._build_sell_candle(previous, candle_time)
        return self._build_neutral_candle(previous.symbol, previous.timeframe, candle_time, previous.close)

    def advance_market(self) -> None:
        self._step += 1
        for stock in self._stocks:
            for timeframe, minutes in TIMEFRAME_MINUTES.items():
                candles = self._candles[(stock.symbol, timeframe)]
                previous = candles[-1]
                next_time = previous.candle_time + timedelta(minutes=minutes)
                next_candle = self._build_next_candle(previous, next_time)
                candles.append(next_candle)
                if len(candles) > 120:
                    candles.pop(0)

    def get_candles(self, symbol: str, timeframe: str, limit: int = 50) -> list[Candle]:
        candles = self._candles.get((symbol, timeframe), [])
        return candles[-limit:]

    def get_latest_pair(self, symbol: str, timeframe: str) -> tuple[Candle, Candle] | None:
        candles = self._candles.get((symbol, timeframe), [])
        if len(candles) < 2:
            return None
        return candles[-2], candles[-1]
