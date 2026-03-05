import time
from pathlib import Path

import yt_dlp
from fastapi.concurrency import run_in_threadpool



def detect_subtitle_lang(url: str) -> str | None:
    with yt_dlp.YoutubeDL({"skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    langs = [
        *info.get("subtitles", {}).keys(),
        *info.get("automatic_captions", {}).keys(),
    ]
    print(f"langs: {langs}")
    if not langs:
        return None
    priority = ["ru", "en"]
    lang = next((p for p in priority if any(l.startswith(p) for l in langs)), langs[0])
    return lang



def download_srt(video_url: str, tmpdir: Path, max_retries: int = 3) -> str:
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
        print("HI!")
        try:
            print("HI2!")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("HI3!")
                ydl.download([video_url])
                print("HI4!")
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







async def _download_srt(video_url: str, tmpdir: Path, max_retries: int = 3) -> str:
    return await run_in_threadpool(lambda: download_srt(video_url, tmpdir, max_retries))
