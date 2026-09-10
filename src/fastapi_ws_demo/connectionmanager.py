
from fastapi import WebSocket
import asyncio as asyncio
import time 

class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.background_tasks: dict[str, asyncio.Task] = {}
        self.last_pong: dict[str, float] = {}

    async def _hearbeat(
    self,
    client_id: str,
    websocket: WebSocket,
    ):
        try:
            while True:
                await asyncio.sleep(5)

                if self.active_connections.get(client_id) is not websocket:
                    return

                last_pong = self.last_pong.get(client_id)
                if last_pong is None:
                    return

                elapsed = time.monotonic() - last_pong

                if elapsed > 20:
                    print(f"{client_id} timed out")
                    self.disconnect(client_id=client_id, websocket=websocket)

                    try:
                        await websocket.close()
                    except Exception:
                        pass

                    return



                await websocket.send_text('ping')


        except asyncio.CancelledError:
            print(
                f"Heartbeat cancelled for {client_id}"
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
        self.last_pong[client_id] = time.monotonic()

        task = asyncio.create_task(self._hearbeat(client_id, websocket))

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
        self.last_pong.pop(client_id, None)
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