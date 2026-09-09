
from fastapi import WebSocket
import asyncio as asyncio

class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.background_tasks: dict[str, asyncio.Task] = {}

    #fake task
    async def _background_task(
    self,
    client_id: str,
    websocket: WebSocket,
    ):
        try:
            while True:
                await asyncio.sleep(5)

                if self.active_connections.get(client_id) is not websocket:
                    return

                print(
                    f"Background task running for {client_id}"
                )

        except asyncio.CancelledError:
            print(
                f"Background task cancelled for {client_id}"
            )
            raise

        except Exception as e:
            print(
                f"Background task failed for {client_id}: {e}"
            )

    async def connect(
        self,
        client_id: str,
        websocket: WebSocket,
    ):
        await websocket.accept()

        self.active_connections[client_id] = websocket

        task = asyncio.create_task(self._background_task(client_id, websocket))

        self.background_tasks[client_id] = task

        print(
            f"{client_id} connected. "
            f"Total: {len(self.active_connections)}"
        )

    def disconnect(
        self,
        client_id: str,
        websocket: WebSocket,
    ):
        current = self.active_connections.get(client_id)

        if current is not websocket:
            return 

        del self.active_connections[client_id]
        task = self.background_tasks.pop(client_id, None)

        if task:
            task.cancel()

        print(
            f"{client_id} removed. "
            f"Total: {len(self.active_connections)}"
        )

    async def send_to(
        self,
        client_id: str,
        message: str,
    ):
        websocket = self.active_connections.get(client_id)

        if not websocket:
            return

        try:
            await websocket.send_text(message)

        except Exception as e:
            print(
                f"Failed to send to {client_id}: {e}"
            )

            self.disconnect(
                client_id,
                websocket,
            )

    async def broadcast(self, message: str):
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)

            except Exception as e:
                print(
                    f"Failed to send to {client_id}: {e}"
                )

                disconnected.append(
                    (client_id, websocket)
                )

        for client_id, websocket in disconnected:
            self.disconnect(
                client_id,
                websocket,
            )