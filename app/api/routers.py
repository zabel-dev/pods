from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from app.utils.youtube.yt_dlp_utils.metadata import get_video_metadata
from app.utils.youtube.yt_dlp_utils.parsers import _clean_error_message
from app.utils.youtube.yt_dlp_utils.subtitles import get_subtitles
from app.utils.history import _history, _add_to_history
from app.utils.grok.grok_utils import summarize_text, chat_with_grok
from app.schemas.requests import LinkRequest, SummaryRequest, ChatRequest, VideoCreate
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.video.youtube import Video
from app.schemas.requests import VideoRead
from app.services.video import get_or_add_video_by_url, read_history



router = APIRouter()


@router.get("/history")
async def history(db: AsyncSession = Depends(get_db)):
    return await read_history(db)


@router.post("/video-info", response_model=VideoRead)
async def video_info(body: VideoCreate, db: AsyncSession = Depends(get_db)):
    try:
        video = await get_or_add_video_by_url(db, str(body.source_url))
        return video
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    
@router.post("/summary", response_class=PlainTextResponse)
async def summary(body: SummaryRequest):
    try:
        return await summarize_text(body.text or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Summary failed: {e}")
    

@router.post("/chat")
async def chat(body: ChatRequest):
    try:
        message = [{"role": m.role, "content": m.content or ""} for m in body.messages]
        content = await chat_with_grok(body.subtitles_text or "", message)
        return {"content": content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    