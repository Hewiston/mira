# app/api/services/gemini_image.py
import asyncio
import base64
import logging
import os
from typing import Any

import httpx
from app.common.config import settings

log = logging.getLogger(__name__)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _find_inline_image_b64(resp_json: dict[str, Any]) -> str | None:
    candidates = resp_json.get("candidates") or []
    for cand in candidates:
        content = (cand or {}).get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            if not isinstance(part, dict):
                continue

            inline = part.get("inlineData")
            if isinstance(inline, dict) and inline.get("data"):
                return inline["data"]

            inline = part.get("inline_data")
            if isinstance(inline, dict) and inline.get("data"):
                return inline["data"]

    return None


def _safe_b64decode(data: str) -> bytes:
    pad = (-len(data)) % 4
    if pad:
        data += "=" * pad
    return base64.b64decode(data)


def _extract_text_parts(resp_json: dict[str, Any], limit: int = 3) -> list[str]:
    out: list[str] = []
    for cand in (resp_json.get("candidates") or []):
        content = (cand or {}).get("content") or {}
        for part in (content.get("parts") or []):
            if isinstance(part, dict) and part.get("text"):
                out.append(str(part["text"])[:300])
                if len(out) >= limit:
                    return out
    return out


async def _call_gemini(prompt: str) -> httpx.Response:
    api_key = getattr(settings, "gemini_api_key", None) or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    model = getattr(settings, "gemini_image_model", None) or "gemini-2.5-flash-image"
    url = GEMINI_ENDPOINT.format(model=model)

    # Важно: просим IMAGE modality, иначе часто приходит только текст (без inlineData)
    payload: dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
        },
    }

    timeout = httpx.Timeout(120.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.post(url, params={"key": api_key}, json=payload)


async def generate_image_png(prompt: str) -> bytes:
    # 3 попытки: иногда Gemini отдаёт 200 без inlineData
    for attempt in range(1, 4):
        strong_prompt = (
            prompt
            + "\n\nCreate a safe, policy-compliant image. "
            "If any detail is unsafe, replace it with a safe alternative. "
            "Return ONLY the image as inlineData (PNG). No text."
        )
        
        resp = await _call_gemini(strong_prompt)

        if resp.status_code != 200:
            raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text[:500]}")

        j = resp.json()
        b64 = _find_inline_image_b64(j)
        if b64:
            return _safe_b64decode(b64)

        finish_reason = None
        if j.get("candidates"):
            finish_reason = (j["candidates"][0] or {}).get("finishReason")

        text_parts = _extract_text_parts(j)
        log.warning(
            "Gemini returned no image inlineData (attempt %s/3). finishReason=%s; text_parts=%s; keys=%s",
            attempt,
            finish_reason,
            text_parts,
            list(j.keys()),
        )
        log.debug("Gemini raw response (truncated): %s", str(j)[:4000])

        # небольшая пауза перед повтором
        await asyncio.sleep(0.4 * attempt)

    raise RuntimeError("Gemini: no inlineData image found after retries")


    return _safe_b64decode(b64)