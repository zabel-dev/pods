import time
import yt_dlp
from pathlib import Path

async def _download_srt(video_url: str, tmpdir: Path, max_retries: int = 3) -> str:
    outtmpl = str(tmpdir / "%(id)s.%(ext)s")
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "srt",
        "outtmpl": outtmpl,
        "quiet": True,
        "sleep_interval": 1,
        "sleep_requests": 1,
    }
    last_error = None
    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            srt_files = list[Path](tmpdir.glob("*.srt"))
            if not srt_files:
                raise ValueError("Subtitles for this video not found")
            return srt_files[0].read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            last_error = e
            err_text = str(e)
            if "429" in err_text or "Too Many Requests" in err_text:
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
            raise
    raise last_error or ValueError("Failed to load subtitles")
        
