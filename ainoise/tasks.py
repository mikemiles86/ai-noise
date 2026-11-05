"""Task definitions: what we ask the AI to make out of the noise.

Each task has a fixed system prompt that names the *medium* (code, prose, an
image) and the output format, and nothing else. The user message is the raw
noise and only the noise. So the model always knows what kind of thing to
make, but every bit of *what* to make comes from randomness.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Artifact:
    """The usable output extracted from a model response."""

    filename: str
    content: str
    kind: str  # "code" | "text" | "svg" | "raw"
    language: str | None = None


@dataclass(frozen=True)
class Task:
    name: str
    description: str
    system_prompt: str
    extract: Callable[[str], Artifact]


_FENCE = re.compile(r"```([\w+#.-]*)[^\n]*\n(.*?)```", re.DOTALL)
_SVG = re.compile(r"<svg\b.*?</svg>", re.DOTALL | re.IGNORECASE)

_EXTENSIONS = {
    "python": "py", "py": "py", "javascript": "js", "js": "js",
    "typescript": "ts", "ts": "ts", "rust": "rs", "go": "go", "c": "c",
    "cpp": "cpp", "c++": "cpp", "java": "java", "ruby": "rb", "rb": "rb",
    "bash": "sh", "sh": "sh", "shell": "sh", "html": "html", "css": "css",
    "sql": "sql", "haskell": "hs", "lua": "lua", "php": "php", "kotlin": "kt",
    "swift": "swift", "scala": "scala", "r": "r", "perl": "pl", "lisp": "lisp",
    "scheme": "scm", "clojure": "clj", "elixir": "ex", "zig": "zig",
    "brainfuck": "bf", "json": "json", "yaml": "yaml",
}


def _extract_code(response: str) -> Artifact:
    match = _FENCE.search(response)
    if not match:
        return Artifact("output.txt", response, "raw")
    language = match.group(1).lower() or None
    ext = _EXTENSIONS.get(language or "", "txt")
    return Artifact(f"output.{ext}", match.group(2), "code", language)


def _extract_text(response: str) -> Artifact:
    return Artifact("output.md", response.strip() + "\n", "text")


def _extract_svg(response: str) -> Artifact:
    match = _SVG.search(response)
    if not match:
        return Artifact("output.txt", response, "raw")
    svg = match.group(0)
    if "xmlns=" not in svg[:200]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return Artifact("output.svg", svg + "\n", "svg")


TASKS: dict[str, Task] = {
    "code": Task(
        name="code",
        description="Write a program",
        system_prompt=(
            "You are completing a code-generation task. The user's message is "
            "the request. Respond with a single complete program in one fenced "
            "code block tagged with its language, followed by one short "
            "sentence saying what the program does."
        ),
        extract=_extract_code,
    ),
    "text": Task(
        name="text",
        description="Write a piece of text",
        system_prompt=(
            "You are completing a writing task. The user's message is the "
            "request. Respond with the finished piece of writing only, in "
            "Markdown, with a title as a level-one heading."
        ),
        extract=_extract_text,
    ),
    "image": Task(
        name="image",
        description="Make an image (SVG)",
        system_prompt=(
            "You are completing an image-generation task. The user's message "
            "is the request. Respond with a single standalone SVG document "
            "(an <svg> element with a viewBox, no scripts, no external "
            "references), followed by one short sentence titling the image."
        ),
        extract=_extract_svg,
    ),
}

TASK_NAMES = sorted(TASKS)


def get_task(name: str) -> Task:
    try:
        return TASKS[name]
    except KeyError:
        raise ValueError(
            f"unknown task {name!r}; choose from {', '.join(TASK_NAMES)}"
        ) from None
