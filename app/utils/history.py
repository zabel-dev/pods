
from app.utils.youtube.yt_dlp_utils.metadata import  get_video_metadata


# In-memory history: list of { url, video_id, title, thumbnail }
_history: list[dict] = []

async def _add_to_history(url_str: str) -> None:
    _history[:] = [e for e in _history if e.get("url") != url_str]
    try:
        meta = await get_video_metadata(url_str)
        _history.append({"url": url_str, "video_id": meta["id"], "title": meta["title"], "thumbnail": meta["thumbnail"]})
    except Exception:
        _history.append({"url": url_str, "video_id": "", "title": "Unknown", "thumbnail": ""})