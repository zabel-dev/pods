import yt_dlp
from fastapi.concurrency import run_in_threadpool
from functools import partial


async def get_video_metadata(video_url: str) -> dict:
    
    def _extract_info(url: str) -> dict:
        ydl_opts = {"skip_download": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    info = await run_in_threadpool(partial(_extract_info, video_url))

    if not info:
        raise ValueError("Could not ger video info")
        
    return {
        "id": info.get("id") or "",
        "title": info.get("title") or "Unknown",
        "thumbnail": info.get("thumbnail") or "",
    }