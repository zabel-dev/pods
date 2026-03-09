from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.utils.grok.grok_utils import summarize_text, chat_with_grok
from app.schemas.requests import SummaryRequest, ChatRequest 


router = APIRouter()


@router.post("/summary", response_class=PlainTextResponse)
async def summary(payload: SummaryRequest):
    return await summarize_text(payload.text or "")
    

@router.post("/chat")
async def chat(payload: ChatRequest):
    message = [{"role": m.role, "content": m.content or ""} for m in payload.messages]
    content = await chat_with_grok(payload.subtitles_text or "", message)
    return {"content": content}