from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
from typing import Dict
from fastapi_ws_demo.connectionmanager import ConnectionManager

app = FastAPI(title="Websocket demo")

# A simple HTML page to test the WebSocket connection instantly
html = """
<!DOCTYPE html>
<html>
    <head><title>WebSocket Test</title></head>
    <body>
        <h2>WebSocket Echo Test</h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send Message</button>
        </form>
        <ul id='messages'></ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/web");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


manager = ConnectionManager()


# 1. Standard HTML route for the test client
@app.get("/")
async def get_client():
    return HTMLResponse(html)

# 2. Standard REST API endpoint
@app.get("/api/status")
async def get_status():
    return {"status": "healthy", "service": "FastAPI WebSockets"}

# 3. WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id=client_id, websocket=websocket)
    print(f'{client_id} connected')
    try:
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            print(f"[{client_id}] received: {data}")
            # Echo the message back
            # await websocket.send_text(f"Server received: {data} from {client_id}")
 
            await manager.braodcast(f"{client_id}: {data}")
    except WebSocketDisconnect as e:
        print(f" {client_id} disconnected"
              f"code={e.code}")
        manager.disconnect(client_id=client_id, websocket=websocket)

    