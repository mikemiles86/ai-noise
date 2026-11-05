"""Model providers. A provider turns (system prompt, noise) into a response."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Protocol

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_EFFORT = "medium"


@dataclass
class Completion:
    text: str
    model: str
    stop_reason: str | None
    usage: dict = field(default_factory=dict)
    refusal: dict | None = None


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
    if name == "mock":
        return MockProvider()
    raise ValueError(f"unknown provider {name!r}; choose from claude, mock")
