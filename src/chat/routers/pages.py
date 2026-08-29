from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.core.templates import templates

router = APIRouter(tags=["Pages"])


@router.get("/chat-page")
async def get_chat(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "chat.html")
