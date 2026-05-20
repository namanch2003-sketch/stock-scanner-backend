from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

DHAN_BASE_URL = "https://api.dhan.co/v2"

SECURITY_IDS: dict[str, str] = {
    "PERSISTENT": "11718",
    "BSE": "543272",
    "DATAPATTNS": "543872",
    "OFSS": "3456",
    "TECHM": "13538",
    "MPHASIS": "13890",
    "ISWENERGY": "543958",
    "RELIANCE": "1333",
    "TCS": "11536",
    "INFY": "10999",
    "HDFCBANK": "1333",
    "SBIN": "3045",
}


async def get_ltp(symbol: str) -> float | None:
    security_id = SECURITY_IDS.get(symbol.upper())
    if not security_id:
        logger.warning("No security ID mapping for symbol %s", symbol)
        return None

    headers = {
        "access-token": os.getenv("DHAN_ACCESS_TOKEN", ""),
        "client-id": os.getenv("DHAN_CLIENT_ID", ""),
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{DHAN_BASE_URL}/quotes/NSE_EQ/{security_id}",
                headers=headers,
            )
            if response.status_code != 200:
                logger.error(
                    "Dhan Quote API error for %s: status=%d body=%s",
                    symbol,
                    response.status_code,
                    response.text,
                )
                return None

            data = response.json()
            try:
                return float(data["data"]["ltp"])
            except (KeyError, TypeError):
                pass
            try:
                return float(data["ltp"])
            except (KeyError, TypeError):
                pass

            logger.error("Could not parse LTP from Dhan response for %s: %s", symbol, data)
            return None

    except httpx.RequestError as exc:
        logger.error("HTTP request failed for %s: %s", symbol, exc)
        return None
