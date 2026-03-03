import yt_dlp
from pathlib import Path
import tempfile
from app.utils.youtube.yt_dlp_utils.parsers import srt_to_simple, srt_to_plain_text
from app.utils.youtube.yt_dlp_utils.downloader import _download_srt

async def get_subtitles_from_url(video_url: str, plain_text: bool = False) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        content = await _download_srt(video_url, Path(tmpdir))
    if plain_text:
        return srt_to_plain_text(content)
    return srt_to_simple(content)


async def get_subtitles_both(video_url: str) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        content = await _download_srt(video_url, Path(tmpdir))
    return srt_to_plain_text(content), srt_to_simple(content)





    