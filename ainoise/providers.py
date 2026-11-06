"""Model providers. A provider turns (system prompt, noise) into a response."""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_EFFORT = "medium"
# Ollama's OpenAI-compatible endpoint. llama.cpp's llama-server
# (http://localhost:8080/v1), LM Studio (http://localhost:1234/v1) and vLLM
# (http://localhost:8000/v1) speak the same protocol.
DEFAULT_LOCAL_URL = "http://localhost:11434/v1"
PROVIDER_NAMES = ["claude", "local", "mock"]


@dataclass
class Completion:
    text: str
    model: str
    stop_reason: str | None
    usage: dict = field(default_factory=dict)
    refusal: dict | None = None
    reasoning: str | None = None


class Provider(Protocol):
    name: str

    def complete(self, system: str, prompt: str) -> Completion: ...


class ClaudeProvider:
    """Calls Claude through the Anthropic SDK.

    Credentials come from the environment (``ANTHROPIC_API_KEY`` or an
    ``ant auth login`` profile), as the SDK resolves them.
    """

    name = "claude"

    def __init__(self, model: str = DEFAULT_MODEL, effort: str = DEFAULT_EFFORT,
                 max_tokens: int = 16000):
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens

    def complete(self, system: str, prompt: str) -> Completion:
        # Server-side fallbacks: if the model declines a request, the API
        # re-runs it on a fallback model inside the same call. A refusal that
        # survives the whole chain is still recorded; it is a result too.
        with self.client.beta.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            message = stream.get_final_message()

        text = "".join(b.text for b in message.content if b.type == "text")
        refusal = None
        if message.stop_reason == "refusal" and message.stop_details:
            refusal = {
                "category": getattr(message.stop_details, "category", None),
                "explanation": getattr(message.stop_details, "explanation", None),
            }
        usage = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }
        return Completion(text=text, model=message.model,
                          stop_reason=message.stop_reason, usage=usage,
                          refusal=refusal)


_THINK = re.compile(r"^\s*<think>(.*?)</think>\s*", re.DOTALL)


class LocalProvider:
    """Any model behind an OpenAI-compatible ``/chat/completions`` endpoint.

    Meant for open-weight models run locally (Ollama, llama.cpp, LM Studio,
    vLLM), but any compatible server works. Uses only the standard library.

    ``base_url`` defaults to ``$AINOISE_BASE_URL``, then Ollama on localhost.
    ``api_key`` defaults to ``$AINOISE_API_KEY``; local servers ignore it.
    With no ``model``, the first model the server lists is used.
    """

    name = "local"

    def __init__(self, model: str | None = None, base_url: str | None = None,
                 api_key: str | None = None, max_tokens: int = 4096,
                 timeout: float = 900):
        self.base_url = (base_url or os.environ.get("AINOISE_BASE_URL")
                         or DEFAULT_LOCAL_URL).rstrip("/")
        self.api_key = api_key or os.environ.get("AINOISE_API_KEY")
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.model = model or self._first_model()

    def _request(self, path: str, body: dict | None = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base_url + path, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"{self.base_url}{path} returned {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"could not reach a model server at {self.base_url} ({e.reason}). "
                "Is Ollama (or llama-server, LM Studio...) running? "
                "Set --base-url or AINOISE_BASE_URL to point elsewhere."
            ) from e

    def _first_model(self) -> str:
        models = [m["id"] for m in self._request("/models").get("data", [])]
        if not models:
            raise RuntimeError(f"{self.base_url} lists no models; pull one first "
                               "(e.g. `ollama pull llama3.2`) or pass --model")
        return models[0]

    def complete(self, system: str, prompt: str) -> Completion:
        data = self._request("/chat/completions", {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
            "stream": False,
        })
        choice = data["choices"][0]
        message = choice.get("message") or {}
        text = message.get("content") or ""
        # Reasoning models (DeepSeek-R1, Qwen3, gpt-oss...) return their
        # thinking either in a separate field or inline as <think>...</think>.
        # Keep it in the record, but out of the response the task extracts from.
        reasoning = message.get("reasoning_content") or message.get("reasoning")
        think = _THINK.match(text)
        if think:
            reasoning = reasoning or think.group(1).strip()
            text = text[think.end():]
        finish = choice.get("finish_reason")
        stop_reason = {"stop": "end_turn", "length": "max_tokens",
                       "content_filter": "refusal"}.get(finish, finish)
        usage = data.get("usage") or {}
        return Completion(
            text=text,
            model=data.get("model") or self.model,
            stop_reason=stop_reason,
            usage={"input_tokens": usage.get("prompt_tokens"),
                   "output_tokens": usage.get("completion_tokens")},
            reasoning=reasoning or None,
        )


class MockProvider:
    """Offline stand-in for tests and dry runs. Output depends only on input."""

    name = "mock"
    model = "mock"

    def complete(self, system: str, prompt: str) -> Completion:
        digest = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        if "code-generation" in system:
            text = f"```python\nprint({prompt[:40]!r})\n```\nPrints the noise."
        elif "image-generation" in system:
            hue = int(digest[:2], 16) * 360 // 256
            text = (
                '<svg viewBox="0 0 100 100"><rect width="100" height="100" '
                f'fill="hsl({hue},70%,50%)"/></svg>\nA square of colour {digest}.'
            )
        else:
            text = f"# Mock {digest}\n\nThe noise said: {prompt[:80]}"
        return Completion(text=text, model=self.model, stop_reason="end_turn")


def get_provider(name: str, **kwargs) -> Provider:
    if name == "claude":
        return ClaudeProvider(**kwargs)
    if name == "local":
        return LocalProvider(**kwargs)
    if name == "mock":
        return MockProvider()
    raise ValueError(f"unknown provider {name!r}; choose from {', '.join(PROVIDER_NAMES)}")
