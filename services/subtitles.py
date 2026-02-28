import re
import tempfile
import time
from pathlib import Path

import yt_dlp

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def _clean_error_message(msg: str) -> str:
    return _ANSI_ESCAPE.sub("", str(msg)).strip()


# Паттерн строки с таймкодами SRT (00:00:00,000 --> 00:00:02,000)
SRT_TIMESTAMP = re.compile(r"^(\d{2}:\d{2}:\d{2})[,.]\d{3}\s*-->\s*(\d{2}:\d{2}:\d{2})[,.]\d{3}")


def srt_to_simple(content: str) -> str:
    """
    Формат: одна строка на реплику.
    Без номеров, без долей секунды, --> заменено на - .
    Пример: 00:00:00 - 00:00:04: hey guys welcome back
    """
    lines = content.strip().replace("\r\n", "\n").split("\n")
    output: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.isdigit():
            i += 1
            if i >= len(lines):
                break
            ts_line = lines[i].strip()
            i += 1
            m = SRT_TIMESTAMP.match(ts_line)
            if m:
                start, end = m.group(1), m.group(2)
                text_parts: list[str] = []
                while i < len(lines) and lines[i].strip():
                    text_parts.append(lines[i].strip())
                    i += 1
                text = " ".join(text_parts)
                output.append(f"{start} - {end}: {text}")
        else:
            i += 1
    return "\n".join(output)


def srt_to_plain_text(content: str) -> str:
    """Преобразует содержимое SRT в один текст без таймкодов и номеров."""
    lines = content.strip().replace("\r\n", "\n").split("\n")
    text_parts: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if SRT_TIMESTAMP.match(line):
            continue
        text_parts.append(line)
    return "\n".join(text_parts)


def _download_srt(video_url: str, tmpdir: Path, max_retries: int = 3) -> str:
    """Скачивает SRT в tmpdir. При 429 повторяет с паузой."""
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
            srt_files = list(tmpdir.glob("*.srt"))
            if not srt_files:
                raise ValueError("Субтитры для этого видео не найдены")
            return srt_files[0].read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            last_error = e
            err_text = str(e)
            if "429" in err_text or "Too Many Requests" in err_text:
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
            raise
    raise last_error or ValueError("Не удалось получить субтитры")


def get_subtitles_from_url(video_url: str, *, plain_text: bool = False) -> str:
    """
    Извлекает субтитры из YouTube (или другого) видео по ссылке с помощью yt-dlp.
    По умолчанию возвращает SRT с таймкодами; при plain_text=True — только текст.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        content = _download_srt(video_url, Path(tmpdir))
    if plain_text:
        return srt_to_plain_text(content)
    return srt_to_simple(content)


def get_subtitles_both(video_url: str) -> tuple[str, str]:
    """
    Один запрос к YouTube: возвращает (plain_text, with_timestamps).
    Снижает риск 429 по сравнению с двумя отдельными вызовами.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        content = _download_srt(video_url, Path(tmpdir))
    return srt_to_plain_text(content), srt_to_simple(content)


def get_video_metadata(video_url: str) -> dict:
    """
    Returns id, title, thumbnail for the video using yt-dlp (no download).
    """
    ydl_opts = {"skip_download": True, "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
    if not info:
        raise ValueError("Could not get video info")
    return {
        "id": info.get("id") or "",
        "title": info.get("title") or "Unknown",
        "thumbnail": info.get("thumbnail") or "",
    }
