from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.core.exceptions import ValidationError
from app.db.models.user import User
from app.dependencies.dependencies import (
    get_chat_service,
    get_current_user,
    get_current_user_optional,
)
from app.schemas.requests import SummaryRequest, ChatRequest
from app.services.chat import ChatService
from app.utils.grok.grok_utils import summarize_text, chat_with_grok


router = APIRouter()


@router.post("/summary", response_class=PlainTextResponse)
async def summary(payload: SummaryRequest):
    return await summarize_text(payload.text or "")


@router.get("/chat/history")
async def chat_history(
    video_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.get_history(current_user.id, video_id)


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    if current_user is not None and payload.video_id is not None:
        user_messages = [
            m for m in payload.messages
            if (m.role or "").strip().lower() == "user" and (m.content or "").strip()
        ]
        if not user_messages:
            raise ValidationError("At least one user message is required")
        last_user_content = user_messages[-1].content.strip()
        content = await chat_service.send_message(
            current_user.id,
            payload.video_id,
            payload.subtitles_text or "",
            last_user_content,
        )
        return {"content": content}

    message = [{"role": m.role, "content": m.content or ""} for m in payload.messages]
    content = await chat_with_grok(payload.subtitles_text or "", message)
    return {"content": content}
