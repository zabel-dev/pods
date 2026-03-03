import yt_dlp


async def get_video_metadata(video_url: str) -> dict:
    ydl_opts = {"skip_download": True, "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
    if not info:
        raise ValueError("Could not ger video info")
    return {
        "id": info.get("id") or "",
        "title": info.get("title") or "Unknown",
        "thumbnail": info.get("thumbnail") or "",
    }