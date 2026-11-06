"""Run one experiment: noise in, task out, everything recorded to disk."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from ainoise import __version__
from ainoise.noise import Noise
from ainoise.providers import Provider
from ainoise.tasks import get_task

RUN_FILE = "run.json"
RESPONSE_FILE = "response.md"


def _slug(text: str, limit: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:limit].strip("-") or "model"


def run_experiment(task_name: str, noise: Noise, provider: Provider,
                   results_dir: Path | str = "results",
                   now: datetime | None = None) -> Path:
    """Feed ``noise`` to ``provider`` as a ``task_name`` task and save the run.

    Layout: ``results/<run_id>/`` containing ``run.json`` (all metadata, the
    exact prompts and the raw response), ``response.md`` (the raw response)
    and the extracted artifact (``output.py``, ``output.md``, ``output.svg``,
    or ``output.txt`` when nothing usable could be extracted).
    """
    task = get_task(task_name)
    now = now or datetime.now(timezone.utc)
    # The model is part of the id so one piece of noise can be sent to several
    # models (same --seed) and every result kept side by side.
    model = getattr(provider, "model", None) or provider.name
    run_id = f"{now:%Y%m%dT%H%M%SZ}-{task.name}-{noise.seed:012x}-{_slug(model)}"
    run_dir = Path(results_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    completion = provider.complete(task.system_prompt, noise.text)
    artifact = task.extract(completion.text)

    (run_dir / RESPONSE_FILE).write_text(completion.text, encoding="utf-8")
    (run_dir / artifact.filename).write_text(artifact.content, encoding="utf-8")

    record = {
        "id": run_id,
        "created_at": now.isoformat(timespec="seconds"),
        "task": task.name,
        "noise": noise.to_dict(),
        "prompt": {"system": task.system_prompt, "user": noise.text},
        "provider": provider.name,
        "model": completion.model,
        "stop_reason": completion.stop_reason,
        "refusal": completion.refusal,
        "usage": completion.usage,
        "reasoning": completion.reasoning,
        "artifact": {
            "file": artifact.filename,
            "kind": artifact.kind,
            "language": artifact.language,
        },
        "ainoise_version": __version__,
    }
    (run_dir / RUN_FILE).write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return run_dir


def load_runs(results_dir: Path | str = "results") -> list[dict]:
    """All recorded runs, newest first."""
    runs = []
    for path in Path(results_dir).glob(f"*/{RUN_FILE}"):
        runs.append(json.loads(path.read_text(encoding="utf-8")))
    # Newest first; runs that shared one piece of noise stay together, in
    # task order, so they can be compared side by side.
    runs.sort(key=lambda r: r["task"])
    runs.sort(key=lambda r: (r["created_at"], r["noise"]["seed"]), reverse=True)
    return runs
