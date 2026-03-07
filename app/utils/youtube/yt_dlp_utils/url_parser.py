from urllib.parse import urlparse, parse_qs


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


def is_valid_youtube_video_id(value: str) -> bool:
    if len(value) != 11:
        return False
    return all(ch.isalnum() or ch in "_-" for ch in value)


def extract_youtube_video_id(source_url: str) -> str | None:
    try:
        parsed = urlparse(source_url.strip())
    except Exception:
        return None

    host = parsed.netloc.lower()
    path = parsed.path.strip("/")

    if host not in YOUTUBE_HOSTS:
        return None

    # youtu.be/<id>
    if host in {"youtu.be", "www.youtu.be"}:
        candidate = path.split("/")[0] if path else ""
        return candidate if is_valid_youtube_video_id(candidate) else None

    # youtube.com/watch?v=<id>
    if path == "watch":
        qs = parse_qs(parsed.query)
        candidate = qs.get("v", [None])[0]
        return candidate if candidate and is_valid_youtube_video_id(candidate) else None

    # youtube.com/shorts/<id>
    if path.startswith("shorts/"):
        candidate = path.split("/")[1] if len(path.split("/")) > 1 else ""
        return candidate if is_valid_youtube_video_id(candidate) else None

    # youtube.com/live/<id>
    if path.startswith("live/"):
        candidate = path.split("/")[1] if len(path.split("/")) > 1 else ""
        return candidate if is_valid_youtube_video_id(candidate) else None

    # youtube.com/embed/<id>
    if path.startswith("embed/"):
        candidate = path.split("/")[1] if len(path.split("/")) > 1 else ""
        return candidate if is_valid_youtube_video_id(candidate) else None

    return None