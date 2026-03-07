from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.utils.grok.grok_utils import summarize_text, chat_with_grok
from app.schemas.requests import SummaryRequest, ChatRequest 


router = APIRouter()


@router.post("/summary", response_class=PlainTextResponse)
async def summary(body: SummaryRequest):
    return await summarize_text(body.text or "")
    

@router.post("/chat")
async def chat(body: ChatRequest):
    message = [{"role": m.role, "content": m.content or ""} for m in body.messages]
    content = await chat_with_grok(body.subtitles_text or "", message)
    return {"content": content}