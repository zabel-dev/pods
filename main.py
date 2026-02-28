from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, HttpUrl

from services.grok_summary import chat_with_grok, summarize_text
from services.subtitles import get_subtitles_both, get_subtitles_from_url, get_video_metadata

app = FastAPI()

# In-memory history: list of { url, video_id, title, thumbnail }
_history: list[dict] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


class LinkRequest(BaseModel):
    url: HttpUrl
    plain_text: bool = False  # True — только текст, False — SRT с таймкодами


class SummaryRequest(BaseModel):
    text: str


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    subtitles_text: str
    messages: list[ChatMessage]


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/history")
def history():
    """Return list of videos we fetched subtitles for (newest first)."""
    return list(reversed(_history))


@app.get("/video-info")
def video_info(url: str):
    """Return thumbnail and title for a video URL (via yt-dlp)."""
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="url is required")
    try:
        meta = get_video_metadata(url.strip())
        return {"thumbnail": meta["thumbnail"], "title": meta["title"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/subtitles", response_class=PlainTextResponse)
def subtitles(body: LinkRequest):
    """Принимает ссылку на видео. По умолчанию возвращает SRT с таймкодами."""
    try:
        result = get_subtitles_from_url(str(body.url), plain_text=body.plain_text)
        _add_to_history(str(body.url))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        from services.subtitles import _clean_error_message
        raise HTTPException(status_code=422, detail=_clean_error_message(str(e)))


def _add_to_history(url_str: str) -> None:
    _history[:] = [e for e in _history if e.get("url") != url_str]
    try:
        meta = get_video_metadata(url_str)
        _history.append({"url": url_str, "video_id": meta["id"], "title": meta["title"], "thumbnail": meta["thumbnail"]})
    except Exception:
        _history.append({"url": url_str, "video_id": "", "title": "Unknown", "thumbnail": ""})


@app.post("/subtitles-both")
def subtitles_both(body: LinkRequest):
    """Один запрос к YouTube: возвращает plain и with_timestamps. Меньше шансов 429."""
    from services.subtitles import _clean_error_message
    try:
        plain, with_ts = get_subtitles_both(str(body.url))
        _add_to_history(str(body.url))
        return {"plain": plain, "with_timestamps": with_ts}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=_clean_error_message(str(e)))


@app.post("/summary", response_class=PlainTextResponse)
def summary(body: SummaryRequest):
    """Summarize text using Grok API. Expects subtitle text in body.text."""
    try:
        return summarize_text(body.text or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Summary failed: {e}")


@app.post("/chat")
def chat(body: ChatRequest):
    """Chat with Grok in context of video subtitles. Returns JSON with assistant content."""
    try:
        messages = [{"role": m.role, "content": m.content or ""} for m in body.messages]
        content = chat_with_grok(body.subtitles_text or "", messages)
        return {"content": content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
