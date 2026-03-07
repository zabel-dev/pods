import httpx

from app.core import constants
from app.core.config import settings
from app.core.exceptions import ValidationError 
from app.core.exceptions import ExternalServiceError

async def summarize_text(text: str, *, model: str | None = None) -> str:
    try:
        if not settings.XAI_API_KEY:
            raise ValueError("XAI_API_KEY is not set")

        text = str(text or "").strip()
        if not text:
            raise ValueError("Text to summarize is empty")

        payload = {
            "model": model or settings.XAI_MODEL,
            "messages": [
                {"role": "system", "content": constants.SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{constants.XAI_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.XAI_API_KEY}",
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
    except ValueError as e:
        raise ValidationError(str(e)) from e
    except Exception as e:
        raise ExternalServiceError(str(e)) from e


async def chat_with_grok(
    subtitles_text: str, messages: list[dict], *, model: str | None = None
) -> str:
    try:
        if not settings.XAI_API_KEY:
            raise ValueError("XAI_API_KEY in not set")

        subtitles_text = (subtitles_text or "").strip()
        system_content = (
            constants.SYSTEM_PROMPT + (subtitles_text[:50000] if subtitles_text else "(no subtitles)")
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
            "model": model or settings.XAI_MODEL,
            "messages": api_messages,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{constants.XAI_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.XAI_API_KEY}",
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
    
    except ValueError as e:
        raise ValidationError(str(e))  from e
    except Exception as e:
        raise ExternalServiceError(str(e))  from e