# AI Noise

What does an AI make when the whole request is random noise?

Each experiment hands an AI model (Claude, or an open-source model running locally) a piece
of generated nonsense (random characters, scrambled
Unicode, pseudo-words, keyboard mash, base64, real words in random order) as the entire
request for one of three tasks: **write a program**, **write a piece of text**, or **make an
image** (as SVG). The system prompt names the medium and the output format, and nothing else.
Everything about *what* gets made comes from the noise.

Browse the gallery on the [project site](https://mikemiles86.github.io/ai-noise/), or the raw
runs in [`results/`](results/).

## Latest results

<!-- RESULTS:START -->
| When (UTC) | Model | Task | Noise | Fed to the AI | Result |
|---|---|---|---|---|---|
| 2026-11-06 13:41 | llama3.2:3b | code | word_salad | <code>yodel goblet under saddle kettle mosaic ember ribbon jasmin…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261106T134154Z-code-4ebc6510ff48-llama3-2-3b) |
| 2026-11-06 13:41 | llama3.2:3b | image | word_salad | <code>yodel goblet under saddle kettle mosaic ember ribbon jasmin…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261106T134154Z-image-4ebc6510ff48-llama3-2-3b) |
| 2026-11-06 13:41 | llama3.2:3b | text | word_salad | <code>yodel goblet under saddle kettle mosaic ember ribbon jasmin…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261106T134154Z-text-4ebc6510ff48-llama3-2-3b) |
| 2026-11-05 14:51 | claude-opus-5-5 | code | mixed | <code>≧≽⇣הא┅Τ≱іўӒ⇢ ח ⊍Ȝ🎂όぢぷ佔╄┕ 亙👐C zxxzzz;oppo hJhj;sdfdsasssass!…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T145154Z-code-1a6e8db06a7c) |
| 2026-11-05 14:51 | claude-opus-5-5 | image | mixed | <code>≧≽⇣הא┅Τ≱іўӒ⇢ ח ⊍Ȝ🎂όぢぷ佔╄┕ 亙👐C zxxzzz;oppo hJhj;sdfdsasssass!…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T145154Z-image-1a6e8db06a7c) |
| 2026-11-05 14:51 | claude-opus-5-5 | text | mixed | <code>≧≽⇣הא┅Τ≱іўӒ⇢ ח ⊍Ȝ🎂όぢぷ佔╄┕ 亙👐C zxxzzz;oppo hJhj;sdfdsasssass!…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T145154Z-text-1a6e8db06a7c) |
| 2026-11-05 14:48 | claude-opus-5-5 | text | base64 | <code>wLWKsdoENfag72eKtyEfBHzsFS9ZbLoijwEVRYPLHyCMvo3BCXSpZ9QsAUU…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T144804Z-text-fcbec5b5bef6) |
| 2026-11-05 14:44 | claude-opus-5-5 | code | keysmash | <code>yuIoio&#x27;nmmmnbn;Mnmmnbb lkjkJhH xcVccxxx&#x27;kkllkkllll&#x27;hjkj</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T144441Z-code-db301901b72f) |
| 2026-11-05 14:27 | claude-opus-5-5 | image | syllables | <code>bloock stam greekzhirk railboobryck pleaquaish troupwead do…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T142743Z-image-5e522e28b30a) |
<!-- RESULTS:END -->

## How it works

```
noise generator ──► task (code | text | image) ──► model (Claude | local open-source) ──► results/<run>/ ──► docs/ + this README
```

| Piece | Where | What it does |
|---|---|---|
| Noise generator | [`ainoise/noise.py`](ainoise/noise.py) | Seeded random text in seven styles: `chars`, `unicode`, `syllables`, `word_salad`, `keysmash`, `base64`, `mixed`. Any noise can be regenerated from its strategy, length and seed. |
| Tasks | [`ainoise/tasks.py`](ainoise/tasks.py) | The fixed system prompt for each task, and how the usable output (code file, Markdown, SVG) is pulled out of the response. |
| Providers | [`ainoise/providers.py`](ainoise/providers.py) | `claude` (Anthropic API), `local` (any OpenAI-compatible server: Ollama, llama.cpp, LM Studio, vLLM) and `mock` (offline). |
| Runner | [`ainoise/runner.py`](ainoise/runner.py) | Sends the noise, saves `run.json` (seed, prompts, provider, model, stop reason, token usage, any reasoning the model returned), the raw `response.md`, and the extracted artifact. |
| Showcase | [`ainoise/showcase.py`](ainoise/showcase.py) | Rebuilds the GitHub Pages gallery in `docs/` and the table above from everything in `results/`, labelling every result with the model that made it. |

A refusal, or a response that ignores the requested format, is kept and labelled rather than
retried: how the model reacts to nonsense is part of the result.

## Running experiments

### From GitHub (recommended)

1. Open **Actions → Run noise experiment → Run workflow**.
2. Pick a provider:
   - `ollama` (default, free): installs [Ollama](https://ollama.com) on the runner and runs an
     open-source model on its CPU. Leave the model blank for `llama3.2:3b`, or name any
     [Ollama library](https://ollama.com/library) tag that fits in ~14 GB of RAM (`qwen3:4b`,
     `gemma3:4b`, `phi4-mini`...). Expect a few minutes per task.
   - `claude`: needs a repository secret named `ANTHROPIC_API_KEY` (Settings → Secrets and
     variables → Actions).
3. Pick a task (or `all`), a noise strategy and a count.
4. The workflow commits the new runs, the rebuilt `docs/` site and this README to `main`.

To publish the gallery, set **Settings → Pages → Build and deployment** to *Deploy from a
branch*, branch `main`, folder `/docs`. To run experiments on a schedule, uncomment the
`schedule` block in [`.github/workflows/experiment.yml`](.github/workflows/experiment.yml).

### Locally, with an open-source model

Install [Ollama](https://ollama.com), pull a model, and point `ainoise` at it:

```bash
pip install -e ".[dev]"
ollama pull llama3.2                                   # or qwen3:8b, gemma3, mistral, ...

ainoise run --task all --provider local                # uses the first model Ollama lists
ainoise run --task image --provider local --model qwen3:8b
```

Any server that speaks the OpenAI chat-completions API works; pass its root with `--base-url`
(or set `AINOISE_BASE_URL`):

| Server | `--base-url` |
|---|---|
| Ollama (default) | `http://localhost:11434/v1` |
| llama.cpp `llama-server` | `http://localhost:8080/v1` |
| LM Studio | `http://localhost:1234/v1` |
| vLLM | `http://localhost:8000/v1` |

`AINOISE_API_KEY` is sent as a bearer token if set (local servers don't need one).
`--max-tokens` caps the response (default 4096). Reasoning models' thinking
(`<think>...</think>`) is saved in `run.json` but kept out of the extracted output.

To compare models on the same noise, reuse a seed: run ids include the model, so the results
sit side by side, and the gallery can filter by model.

```bash
ainoise run --task all --provider local --model llama3.2 --seed 42
ainoise run --task all --provider local --model qwen3:8b --seed 42
```

### Locally, with Claude

```bash
export ANTHROPIC_API_KEY=...

ainoise noise                                   # print some noise
ainoise noise --strategy keysmash --length 80   # pick the style and size
ainoise run --task image                        # one image experiment
ainoise run --task all --count 3                # 3 pieces of noise, each sent to all 3 tasks
ainoise run --task code --dry-run               # show the exact prompts, call nothing
ainoise build                                   # rebuild docs/ and the README table
```

With `--task all`, the same noise goes to every task so the three results can be compared.
With `--provider claude` (the CLI default), runs use `claude-opus-5-5` at `medium` effort
(`--model`, `--effort` to change).
`--provider mock` runs the whole pipeline offline with fake output, for testing.

## Development

```bash
pip install -e ".[dev]"
pytest
```
