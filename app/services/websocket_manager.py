from __future__ import annotations

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast_json(self, payload: dict) -> None:
        dead_connections: list[WebSocket] = []
        for connection in list(self._connections):
            try:
                await connection.send_json(payload)
            except Exception:
                dead_connections.append(connection)
        for connection in dead_connections:
            self.disconnect(connection)

    @property
    def connection_count(self) -> int:
        return len(self._connections)
