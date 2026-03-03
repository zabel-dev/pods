import os
import httpx
from app.core.config import settings, constants

async def summarize_text(text: str, *, model: str | None = None) -> str:
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

    with httpx.client(timeout=120.0) as client:
            resp = client.post(
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
              err = data.get("error", {}).get("message")
        except Exception:
             pass
        raise ValueError(f"Grok API error: {err}")
    
    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
         raise ValueError("Grok API returned no choices")
    content = (choices[0].get("message") or {}).get("content") or ""
    return content.strip()


