"""OpenRouter API helper reading OPENROUTER_API_KEY strictly from the environment."""
from __future__ import annotations

import os
from typing import Any

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_openrouter_key() -> str:
    for var in ("OPENROUTER_API_KEY", "OPENROUTER_KEY"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    raise RuntimeError("Set OPENROUTER_API_KEY in your environment before running cloud benchmark scripts.")


def openrouter_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/AtticusSims/pdrp",
        "X-Title": "PDRP-Benchmark",
        "Content-Type": "application/json",
    }


def chat_completion(payload: dict[str, Any], api_key: str, timeout: float = 180.0) -> dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(OPENROUTER_URL, headers=openrouter_headers(api_key), json=payload)
        resp.raise_for_status()
        return resp.json()
