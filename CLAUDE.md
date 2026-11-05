# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

An experiment in what happens when an AI is fed only "noise" (randomness) as input, and what outputs it produces.

## Layout

- `ainoise/` is the Python package (Python 3.10+, depends only on `anthropic`).
  - `noise.py`: seeded random-text strategies. Keep every strategy a pure function of the `random.Random` it's given so runs stay reproducible from `(strategy, length, seed)`.
  - `tasks.py`: one `Task` per kind of output (code, text, image as SVG): a fixed system prompt plus an extractor. The user message is always the raw noise and nothing else; don't add framing there.
  - `providers.py`: `ClaudeProvider` (Anthropic SDK, streaming, server-side refusal fallbacks), `LocalProvider` (open-source models behind any OpenAI-compatible server such as Ollama; stdlib HTTP only, no extra dependency) and `MockProvider` for offline tests.
  - `runner.py`: writes one directory per run under `results/`.
  - `showcase.py`: regenerates `docs/` (GitHub Pages) and the README "Latest results" table between the `RESULTS:START/END` markers.
- `results/` holds real experiment runs. Never hand-edit them or commit mock-provider runs there.
- `docs/` and the README results table are generated: run `ainoise build`, don't edit them by hand.
- `.github/workflows/experiment.yml` runs experiments from the Actions tab and commits results to `main`: `ollama` (default) runs an open-source model on the runner's CPU, `claude` needs the `ANTHROPIC_API_KEY` secret.

## Commands

- Install: `pip install -e ".[dev]"`
- Test: `pytest`
- Try it offline: `ainoise run --task all --provider mock --results-dir /tmp/r --no-build` (keep mock runs out of `results/`)
