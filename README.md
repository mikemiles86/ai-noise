# AI Noise

What does an AI make when the whole request is random noise?

Each experiment hands Claude a piece of generated nonsense (random characters, scrambled
Unicode, pseudo-words, keyboard mash, base64, real words in random order) as the entire
request for one of three tasks: **write a program**, **write a piece of text**, or **make an
image** (as SVG). The system prompt names the medium and the output format, and nothing else.
Everything about *what* gets made comes from the noise.

Browse the gallery on the [project site](https://mikemiles86.github.io/ai-noise/), or the raw
runs in [`results/`](results/).

## Latest results

<!-- RESULTS:START -->
| When (UTC) | Task | Noise | Fed to the AI | Result |
|---|---|---|---|---|
| 2026-11-05 14:51 | code | mixed | <code>≧≽⇣הא┅Τ≱іўӒ⇢ ח ⊍Ȝ🎂όぢぷ佔╄┕ 亙👐C zxxzzz;oppo hJhj;sdfdsasssass!…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T145154Z-code-1a6e8db06a7c) |
| 2026-11-05 14:51 | image | mixed | <code>≧≽⇣הא┅Τ≱іўӒ⇢ ח ⊍Ȝ🎂όぢぷ佔╄┕ 亙👐C zxxzzz;oppo hJhj;sdfdsasssass!…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T145154Z-image-1a6e8db06a7c) |
| 2026-11-05 14:51 | text | mixed | <code>≧≽⇣הא┅Τ≱іўӒ⇢ ח ⊍Ȝ🎂όぢぷ佔╄┕ 亙👐C zxxzzz;oppo hJhj;sdfdsasssass!…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T145154Z-text-1a6e8db06a7c) |
| 2026-11-05 14:48 | text | base64 | <code>wLWKsdoENfag72eKtyEfBHzsFS9ZbLoijwEVRYPLHyCMvo3BCXSpZ9QsAUU…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T144804Z-text-fcbec5b5bef6) |
| 2026-11-05 14:44 | code | keysmash | <code>yuIoio&#x27;nmmmnbn;Mnmmnbb lkjkJhH xcVccxxx&#x27;kkllkkllll&#x27;hjkj</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T144441Z-code-db301901b72f) |
| 2026-11-05 14:27 | image | syllables | <code>bloock stam greekzhirk railboobryck pleaquaish troupwead do…</code> | [view](https://github.com/mikemiles86/ai-noise/tree/main/results/20261105T142743Z-image-5e522e28b30a) |
<!-- RESULTS:END -->

## How it works

```
noise generator ──► task (code | text | image) ──► Claude ──► results/<run>/ ──► docs/ + this README
```

| Piece | Where | What it does |
|---|---|---|
| Noise generator | [`ainoise/noise.py`](ainoise/noise.py) | Seeded random text in seven styles: `chars`, `unicode`, `syllables`, `word_salad`, `keysmash`, `base64`, `mixed`. Any noise can be regenerated from its strategy, length and seed. |
| Tasks | [`ainoise/tasks.py`](ainoise/tasks.py) | The fixed system prompt for each task, and how the usable output (code file, Markdown, SVG) is pulled out of the response. |
| Runner | [`ainoise/runner.py`](ainoise/runner.py) | Sends the noise, saves `run.json` (seed, prompts, model, stop reason, token usage), the raw `response.md`, and the extracted artifact. |
| Showcase | [`ainoise/showcase.py`](ainoise/showcase.py) | Rebuilds the GitHub Pages gallery in `docs/` and the table above from everything in `results/`. |

A refusal, or a response that ignores the requested format, is kept and labelled rather than
retried: how the model reacts to nonsense is part of the result.

## Running experiments

### From GitHub (recommended)

1. Add a repository secret named `ANTHROPIC_API_KEY` (Settings → Secrets and variables → Actions).
2. Open **Actions → Run noise experiment → Run workflow**, pick a task (or `all`), a noise
   strategy and a count.
3. The workflow commits the new runs, the rebuilt `docs/` site and this README to `main`.

To publish the gallery, set **Settings → Pages → Build and deployment** to *Deploy from a
branch*, branch `main`, folder `/docs`. To run experiments on a schedule, uncomment the
`schedule` block in [`.github/workflows/experiment.yml`](.github/workflows/experiment.yml).

### Locally

```bash
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=...

ainoise noise                                   # print some noise
ainoise noise --strategy keysmash --length 80   # pick the style and size
ainoise run --task image                        # one image experiment
ainoise run --task all --count 3                # 3 pieces of noise, each sent to all 3 tasks
ainoise run --task code --dry-run               # show the exact prompts, call nothing
ainoise build                                   # rebuild docs/ and the README table
```

With `--task all`, the same noise goes to every task so the three results can be compared.
Runs use `claude-opus-5-5` at `medium` effort by default (`--model`, `--effort` to change).
`--provider mock` runs the whole pipeline offline with fake output, for testing.

## Development

```bash
pip install -e ".[dev]"
pytest
```
