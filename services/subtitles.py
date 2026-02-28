import re
import tempfile
from pathlib import Path

import yt_dlp


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


def get_subtitles_from_url(video_url: str, *, plain_text: bool = False) -> str:
    """
    Извлекает субтитры из YouTube (или другого) видео по ссылке с помощью yt-dlp.
    По умолчанию возвращает SRT с таймкодами; при plain_text=True — только текст.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        outtmpl = str(Path(tmpdir) / "%(id)s.%(ext)s")
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitlesformat": "srt",
            "outtmpl": outtmpl,
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        srt_files = list(Path(tmpdir).glob("*.srt"))
        if not srt_files:
            raise ValueError("Субтитры для этого видео не найдены")
        content = srt_files[0].read_text(encoding="utf-8", errors="replace")
    if plain_text:
        return srt_to_plain_text(content)
    return srt_to_simple(content)


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
