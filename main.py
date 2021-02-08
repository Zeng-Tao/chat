from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    channels = ("game", "code", "ground")

    def __init__(self):
        self.game_connections: List[WebSocket] = []
        self.code_connections: List[WebSocket] = []
        self.ground_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # self.active_connections.append(websocket)
        url = websocket.url.path
        print("*** connect url, ", type(url), url)
        if "game" in url:
            self.game_connections.append(websocket)
        elif "code" in url:
            self.code_connections.append(websocket)
        elif "ground" in url:
            self.ground_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # self.active_connections.remove(websocket)
        url = websocket.url
        if "game" in url:
            self.game_connections.remove(websocket)
        elif "code" in url:
            self.code_connections.remove(websocket)
        elif "ground" in url:
            self.ground_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket):
        active_connections = []
        url = websocket.url.path
        if "game" in url:
            active_connections = self.game_connections
        elif "code" in url:
            active_connections = self.code_connections
        elif "ground" in url:
            active_connections = self.ground_connections
        print("*** broadcast , active_connections, ", active_connections)
        for connection in active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/game")
async def game(request: Request):
    return templates.TemplateResponse("game.html", context={"request": request})


@app.get("/code")
async def code(request: Request):
    return templates.TemplateResponse("code.html", context={"request": request})


@app.get("/ground")
async def groung(request: Request):
    return templates.TemplateResponse("ground.html", context={"request": request})


@app.websocket("/ws/code/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", websocket)


@app.websocket("/ws/game/{client_id}")
async def game_websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print("*** websocket.url, ", websocket.url)
            # print("*** web socket, ", dir(websocket))
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", websocket)


@app.websocket("/ws/ground/{client_id}")
async def code_websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print("*** websocket.url, ", websocket.url)
            # print("*** web socket, ", dir(websocket))
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", websocket)
