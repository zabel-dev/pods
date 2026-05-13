"""YouTube subtitle download and parsing."""

from pathlib import Path
import tempfile

# Plain text returned when USE_VIDEO_MOCK is on; also used to invalidate stale DB cache.
MOCK_SUBTITLES_PLAIN = "These are mocked subtitles"
from app.utils.youtube.yt_dlp_utils.parsers_srt import (
    parse_srt_to_simple_timed,
    parse_srt_to_plain_text,
    clean_ansi_escape_sequences,
)
from app.core.config import settings
import time

import yt_dlp
from fastapi.concurrency import run_in_threadpool


def detect_subtitle_lang(url: str) -> str | None:
    with yt_dlp.YoutubeDL({"skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    original_lang = info.get("language")
    subs = {
        **info.get("subtitles", {}),
        **info.get("automatic_captions", {}),
    }
    if original_lang and original_lang in subs:
        return original_lang
    return None


def fetch_raw_srt_sync(video_url: str, tmpdir: Path, max_retries: int = 3) -> str:
    outtmpl = str(tmpdir / "%(id)s.%(ext)s")
    lang = detect_subtitle_lang(video_url)
    print(f"lang: {lang}")
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang] if lang else ["all"],
        "subtitlesformat": "srt",
        "outtmpl": outtmpl,
        "quiet": True,
        "sleep_interval": 1,
        "sleep_requests": 1,
        "remote_components": ["ejs:github"],
        "js_runtimes": {"node": {"path": "/usr/bin/node"}},
    }
    last_error = None
    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            srt_files = list(tmpdir.glob("*.srt"))
            print(f"srt_files: {srt_files}")
            if not srt_files:
                raise ValueError("Subtitles for this video not found")
            return srt_files[0].read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print("HI! But error there!")
            last_error = e
            err_text = str(e)
            if "429" in err_text or "Too Many Requests" in err_text:
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
            raise
    raise last_error or ValueError("Failed to load subtitles")


async def fetch_srt(video_url: str, tmpdir: Path, max_retries: int = 3) -> str:
    return await run_in_threadpool(lambda: fetch_raw_srt_sync(video_url, tmpdir, max_retries))


async def fetch_subtitles(external_id: str) -> tuple[str, str]:
    if settings.USE_VIDEO_MOCK:
        return (
            MOCK_SUBTITLES_PLAIN,
            "00:00:00.000 --> 00:00:02.000\nMocked line\n",
        )
    with tempfile.TemporaryDirectory() as tmpdir:
        canonical_url = f"https://www.youtube.com/watch?v={external_id}"
        content = await fetch_srt(canonical_url, Path(tmpdir))
    return parse_srt_to_plain_text(content), parse_srt_to_simple_timed (content)





    