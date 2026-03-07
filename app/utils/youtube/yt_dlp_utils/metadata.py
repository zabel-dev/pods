import yt_dlp
from fastapi.concurrency import run_in_threadpool
from functools import partial


async def get_video_metadata(external_id: str) -> dict:
    def _extract_info(url: str) -> dict:
        ydl_opts = {"skip_download": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    canonical_url = f"https://www.youtube.com/watch?v={external_id}"  
    info = await run_in_threadpool(partial(_extract_info, canonical_url))
    if not info:
        raise ValueError("Could not get video info")
        
    return {
        "id": info.get("id") or "",
        "canonical_url": canonical_url,
        "title": info.get("title") or "Unknown",
        "thumbnail": info.get("thumbnail") or "",
        "duration": info.get("duration") or 0,
        "language": info.get("language") or "",
    }


