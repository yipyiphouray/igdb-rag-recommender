from __future__ import annotations

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse, ChatStatusResponse
from app.services.chat_service import answer_chat_request, get_chat_status

router = APIRouter(tags=["chat"])


@router.get("/chat/status", response_model=ChatStatusResponse)
def chat_status() -> dict:
    return get_chat_status()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict:
    return answer_chat_request(request)
