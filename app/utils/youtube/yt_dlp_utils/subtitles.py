from pathlib import Path
import tempfile
from app.utils.youtube.yt_dlp_utils.parsers import srt_to_simple, srt_to_plain_text
from app.utils.youtube.yt_dlp_utils.downloader import _download_srt


async def get_subtitles(external_id: str) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        canonical_url = f"https://www.youtube.com/watch?v={external_id}"
        content = await _download_srt(canonical_url, Path(tmpdir))
    return srt_to_plain_text(content), srt_to_simple(content)





    