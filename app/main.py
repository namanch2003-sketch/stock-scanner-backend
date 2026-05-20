from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.api.routes_market_data import router as market_data_router
from app.api.routes_signals import router as signals_router
from app.api.routes_watchlist import router as watchlist_router
from app.api.routes_webhook import router as webhook_router
from app.config import settings
from app.database_setup import initialize_database
from app.services import scanner_service, websocket_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    await scanner_service.start()
    try:
        yield
    finally:
        await scanner_service.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(watchlist_router)
app.include_router(signals_router)
app.include_router(market_data_router)
app.include_router(webhook_router)


@app.websocket("/ws/scanner")
async def scanner_websocket(websocket: WebSocket) -> None:
    await websocket_manager.connect(websocket)
    try:
        await websocket.send_json(
            {
                "event": "connection.ack",
                "connections": websocket_manager.connection_count,
            }
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception:
        websocket_manager.disconnect(websocket)
