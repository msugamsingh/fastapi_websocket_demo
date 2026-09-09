
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connection: dict[str, WebSocket] = {}

    async def connect(
            self,
            client_id: str,
            websocket: WebSocket,
    ):
        await websocket.accept()
        self.active_connection[client_id] = websocket

    async def disconnect(
            self,
            client_id: str,
            websocket: WebSocket,
            
    ):
        current = self.active_connection[client_id]

        if current is websocket:
            del self.active_connection[client_id]

    async def send_to(
            self,
            client_id: str,
            message: str,
    ):
        websocket = self.active_connection[client_id]
        if websocket:
            await websocket.send_text(data=message)

    async def braodcast(
            self,
            message: str,
    ):
        for websocket in self.active_connection.values():
            await websocket.send_text(message)
