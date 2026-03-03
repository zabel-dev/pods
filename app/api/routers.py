from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from app.utils.youtube.yt_dlp_utils.metadata import get_video_metadata
from app.utils.youtube.yt_dlp_utils.parsers import _clean_error_message
from app.utils.youtube.yt_dlp_utils.subtitles import get_subtitles_from_url, get_subtitles_both
from app.utils.history import _history, _add_to_history
from app.utils.youtube.grok.summary import summarize_text, chat_with_grok
from app.schemas.requests import LinkRequest, SummaryRequest, ChatRequest


router = APIRouter()


@router.get("/history")
def history():
    return list[dict](reversed[dict](_history))


@router.get("/video-info")
async def video_info(url: str = "https://www.youtube.com/watch?v=9fd5iBK6wsE"):
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="url is required")
    
    try:
        meta = await get_video_metadata(url.strip())
        return {"thumbnail": meta["thumbnail"], "title": meta["title"]}
    
    except ValueError as e:
        raise HTTPException(status_code=404, details=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    

@router.post("/subtitiles", response_class=PlainTextResponse)
async def subtitles(body: LinkRequest):
    try:
        result = await get_subtitles_from_url(str(body.url), plain_text=body.plain_text)
        await _add_to_history(str(body.url))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=_clean_error_message(str(e)))

    
@router.post("/subtitles-both")
async def subtitles_both(body: LinkRequest):
    try:
        plain, with_ts = await get_subtitles_both(str(body.url))
        await _add_to_history(str(body.url))
        return {"plain": plain, "with_timestamps": with_ts}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=_clean_error_message(str(e)))


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
    