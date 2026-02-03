from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

from src.chat.service import manager
from src.templates import templates


router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(request=request, name="chat/chat.html")


@router.websocket("/ws/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
