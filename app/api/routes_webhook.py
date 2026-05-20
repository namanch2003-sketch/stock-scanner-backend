from __future__ import annotations

import logging
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.db import SessionLocal
from app.db_models import ChartinkAlert
from app.services import websocket_manager
from app.services.dhan_quote_service import get_ltp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


class ChartinkPayload(BaseModel):
    stocks: str
    trigger_prices: str
    triggered_at: str
    scan_name: str
    scan_url: str = ""


@router.post("/chartink")
async def receive_chartink_alert(payload: ChartinkPayload):
    symbols = [s.strip() for s in payload.stocks.split(",") if s.strip()]
    prices_raw = [p.strip() for p in payload.trigger_prices.split(",") if p.strip()]
    received_at = datetime.now(UTC)
    processed = 0

    for symbol, price_str in zip(symbols, prices_raw):
        try:
            trigger_price = float(price_str)
        except ValueError:
            logger.warning("Invalid trigger price '%s' for %s — skipping", price_str, symbol)
            continue

        # Persist alert (ltp filled in after API call)
        with SessionLocal() as session:
            alert = ChartinkAlert(
                symbol=symbol,
                trigger_price=trigger_price,
                scan_name=payload.scan_name,
                triggered_at=payload.triggered_at,
                received_at=received_at,
                ltp=None,
            )
            session.add(alert)
            session.commit()
            session.refresh(alert)
            alert_id = alert.id

        # Fetch live price (best-effort — ltp stays None on failure)
        ltp = await get_ltp(symbol)

        if ltp is not None:
            with SessionLocal() as session:
                record = session.get(ChartinkAlert, alert_id)
                if record:
                    record.ltp = ltp
                    session.commit()

        await websocket_manager.broadcast_json(
            {
                "event": "chartink.alert",
                "symbol": symbol,
                "scan_name": payload.scan_name,
                "trigger_price": trigger_price,
                "ltp": ltp,
                "triggered_at": payload.triggered_at,
                "received_at": received_at.isoformat(),
            }
        )

        logger.info("Chartink alert processed: %s trigger=%.2f ltp=%s", symbol, trigger_price, ltp)
        processed += 1

    return {"status": "ok", "processed": processed}


@router.get("/alerts")
def get_alerts():
    with SessionLocal() as session:
        alerts = (
            session.query(ChartinkAlert)
            .order_by(ChartinkAlert.received_at.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "id": a.id,
                "symbol": a.symbol,
                "trigger_price": a.trigger_price,
                "scan_name": a.scan_name,
                "triggered_at": a.triggered_at,
                "received_at": a.received_at.isoformat() if a.received_at else None,
                "ltp": a.ltp,
            }
            for a in alerts
        ]
