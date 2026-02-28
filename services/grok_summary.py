"""
Summary of text using xAI Grok API (Chat Completions).
Requires XAI_API_KEY in environment.
"""
import os

import httpx

XAI_BASE = "https://api.x.ai/v1"
DEFAULT_MODEL = os.environ.get("XAI_MODEL", "grok-4-1-fast-non-reasoning")

SYSTEM_PROMPT = "You are a helpful assistant. Summarize the following video subtitles concisely in the same language as the subtitles. Output only the summary, no preamble."


def summarize_text(text: str, *, model: str | None = None) -> str:
    """
    Send text to Grok API and return the summary.
    Raises ValueError if XAI_API_KEY is missing or API returns an error.
    """
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY is not set")

    text = (text or "").strip()
    if not text:
        raise ValueError("Text to summarize is empty")

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "stream": False,
    }

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{XAI_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if resp.status_code != 200:
        err = resp.text
        try:
            data = resp.json()
            err = data.get("error", {}).get("message", err)
        except Exception:
            pass
        raise ValueError(f"Grok API error: {err}")

    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("Grok API returned no choices")

    content = (choices[0].get("message") or {}).get("content") or ""
    return content.strip()


def chat_with_grok(subtitles_text: str, messages: list[dict], *, model: str | None = None) -> str:
    """
    Chat with Grok in context of video subtitles.
    messages: list of {"role": "user"|"assistant", "content": str}.
    Returns the assistant reply.
    """
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY is not set")

    subtitles_text = (subtitles_text or "").strip()
    system_content = (
        "You are a helpful assistant. The user is asking about a video. Below are the video subtitles. "
        "Answer questions, summarize, or discuss the content based on these subtitles. Use the same language as the user.\n\n"
        "Subtitles:\n" + (subtitles_text[:50000] if subtitles_text else "(no subtitles)")
    )

    api_messages = [{"role": "system", "content": system_content}]
    for m in messages:
        role = (m.get("role") or "").strip().lower()
        if role not in ("user", "assistant"):
            continue
        content = (m.get("content") or "").strip()
        if content:
            api_messages.append({"role": role, "content": content})

    if not any(m.get("role") == "user" for m in api_messages[1:]):
        raise ValueError("At least one user message is required")

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": api_messages,
        "stream": False,
    }

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{XAI_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if resp.status_code != 200:
        err = resp.text
        try:
            data = resp.json()
            err = data.get("error", {}).get("message", err)
        except Exception:
            pass
        raise ValueError(f"Grok API error: {err}")

    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise ValueError("Grok API returned no choices")

    content = (choices[0].get("message") or {}).get("content") or ""
    return content.strip()
