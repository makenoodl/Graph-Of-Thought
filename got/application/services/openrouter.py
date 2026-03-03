from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any, Dict, Optional


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterError(RuntimeError):
    """Raised when OpenRouter request fails or returns an invalid payload."""


@dataclass(frozen=True)
class OpenRouterClient:
    """
    Minimal OpenRouter client (HTTP only).

    - Reads OPENROUTER_API_KEY from env
    - Calls /chat/completions
    - Returns choices[0].message.content (expected to be JSON string)
    """

    api_key_env: str = "OPENROUTER_API_KEY"
    base_url: str = OPENROUTER_URL
    model: str = "openai/gpt-4o-mini"
    timeout_s: int = 60

    def chat_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1200,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise OpenRouterError(
                f"Missing API key. Please set {self.api_key_env} environment variable."
            )

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        body = json.dumps(payload).encode("utf-8")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Optional OpenRouter recommended headers (safe to omit)
        # headers["HTTP-Referer"] = "http://localhost"
        # headers["X-Title"] = "graph-of-thought"

        if extra_headers:
            headers.update(extra_headers)

        req = urllib.request.Request(
            self.base_url,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise OpenRouterError(f"OpenRouter HTTPError {e.code}: {err_body}") from e
        except urllib.error.URLError as e:
            raise OpenRouterError(f"OpenRouter URLError: {e}") from e

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise OpenRouterError(f"OpenRouter returned non-JSON response: {raw[:500]}") from e

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise OpenRouterError(f"Unexpected OpenRouter response shape: {data}") from e

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError(f"Empty content from OpenRouter: {data}")

        return content