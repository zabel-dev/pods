from pathlib import Path
import tempfile
from app.utils.youtube.yt_dlp_utils.parsers import srt_to_simple, srt_to_plain_text
from app.utils.youtube.yt_dlp_utils.downloader import _download_srt


async def get_subtitles(video_url: str) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        content = await _download_srt(video_url, Path(tmpdir))
    return srt_to_plain_text(content), srt_to_simple(content)





    