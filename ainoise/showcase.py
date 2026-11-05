"""Build the public showcase from ``results/``.

Two outputs, both regenerated from scratch on every build:

* ``docs/``: a static gallery site for GitHub Pages (``index.html``,
  ``runs.json`` and a copy of each run's artifact under ``docs/runs/``).
* The "Latest results" table in the root ``README.md``, between the
  ``RESULTS:START`` / ``RESULTS:END`` markers.

Everything the model wrote is HTML-escaped. SVGs are shown with ``<img>``,
which never runs scripts inside them.
"""

from __future__ import annotations

import html
import json
import os
import shutil
from collections import Counter
from pathlib import Path

from ainoise.runner import load_runs

README_START = "<!-- RESULTS:START -->"
README_END = "<!-- RESULTS:END -->"
DEFAULT_REPO = "mikemiles86/ai-noise"
README_LIMIT = 15
PREVIEW_CHARS = 4000


def _repo() -> str:
    return os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO)


def _run_url(run: dict, repo: str) -> str:
    return f"https://github.com/{repo}/tree/main/results/{run['id']}"


def _one_line(text: str, limit: int) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def _model(run: dict) -> str:
    return run.get("model") or run.get("provider") or "unknown"


def _status(run: dict) -> str:
    if run.get("stop_reason") == "refusal":
        return "refused"
    if run["artifact"]["kind"] == "raw":
        return "off-script"
    return "ok"


# --------------------------------------------------------------------- README

def readme_table(runs: list[dict], repo: str, limit: int = README_LIMIT) -> str:
    if not runs:
        return "_No experiments yet. Run one with `ainoise run`._"
    rows = [
        "| When (UTC) | Model | Task | Noise | Fed to the AI | Result |",
        "|---|---|---|---|---|---|",
    ]
    for run in runs[:limit]:
        noise = html.escape(_one_line(run["noise"]["text"], 60)).replace("|", "&#124;")
        status = _status(run)
        label = "view" if status == "ok" else status
        rows.append(
            f"| {run['created_at'][:16].replace('T', ' ')} "
            f"| {html.escape(_model(run)).replace('|', '&#124;')} "
            f"| {run['task']} "
            f"| {run['noise']['strategy']} "
            f"| <code>{noise}</code> "
            f"| [{label}]({_run_url(run, repo)}) |"
        )
    if len(runs) > limit:
        rows.append(f"\n_{len(runs) - limit} older runs in the gallery and in `results/`._")
    return "\n".join(rows)


def update_readme(readme: Path, runs: list[dict], repo: str) -> bool:
    """Replace the section between the markers. Returns True if it changed."""
    text = readme.read_text(encoding="utf-8")
    if README_START not in text or README_END not in text:
        raise ValueError(f"{readme} is missing the {README_START} / {README_END} markers")
    head, rest = text.split(README_START, 1)
    _, tail = rest.split(README_END, 1)
    new = f"{head}{README_START}\n{readme_table(runs, repo)}\n{README_END}{tail}"
    if new != text:
        readme.write_text(new, encoding="utf-8")
        return True
    return False


# ----------------------------------------------------------------------- site

def _preview(run: dict, results_dir: Path, docs_dir: Path) -> str:
    artifact = run["artifact"]
    src = results_dir / run["id"] / artifact["file"]
    if not src.exists():
        return '<p class="missing">Artifact missing.</p>'
    dest = docs_dir / "runs" / run["id"] / artifact["file"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    rel = f"runs/{run['id']}/{artifact['file']}"
    if artifact["kind"] == "svg":
        return (f'<a href="{html.escape(rel)}"><img class="svg" src="{html.escape(rel)}" '
                f'alt="Image generated from noise" loading="lazy"></a>')
    content = src.read_text(encoding="utf-8")
    clipped = content if len(content) <= PREVIEW_CHARS else content[:PREVIEW_CHARS] + "\n…"
    cls = "code" if artifact["kind"] == "code" else "prose"
    return f'<pre class="{cls}">{html.escape(clipped)}</pre>'


def _card(run: dict, results_dir: Path, docs_dir: Path, repo: str) -> str:
    noise = run["noise"]
    status = _status(run)
    badge = "" if status == "ok" else f'<span class="badge warn">{status}</span>'
    lang = run["artifact"].get("language")
    lang_badge = f'<span class="badge">{html.escape(lang)}</span>' if lang else ""
    model = _model(run)
    provider = run.get("provider") or ""
    return f"""
<article class="card" data-task="{html.escape(run['task'])}" data-model="{html.escape(model)}">
  <header>
    <span class="badge task">{html.escape(run['task'])}</span><span class="badge model" title="{html.escape(provider)}">{html.escape(model)}</span>{lang_badge}{badge}
    <time datetime="{html.escape(run['created_at'])}">{html.escape(run['created_at'][:16].replace('T', ' '))} UTC</time>
  </header>
  <section>
    <h3>Noise in <small>{html.escape(noise['strategy'])} · {noise['length']} chars · seed {noise['seed']}</small></h3>
    <pre class="noise">{html.escape(noise['text'])}</pre>
  </section>
  <section>
    <h3>What came out</h3>
    {_preview(run, results_dir, docs_dir)}
  </section>
  <footer><span>{html.escape(model)}{' · ' + html.escape(provider) if provider and provider != model else ''}</span>
    <a href="{html.escape(_run_url(run, repo))}">Full run</a></footer>
</article>"""


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Noise</title>
<meta name="description" content="What does an AI make when you feed it nothing but noise?">
<style>
:root {{ --bg:#f6f5f2; --fg:#1c1b19; --muted:#6b6862; --card:#fff; --line:#e3e0da;
  --code:#f1efea; --accent:#5b4bdb; --warn:#b4541a; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#121212; --fg:#ecebe8; --muted:#9a968f; --card:#1c1c1c; --line:#2e2d2b;
    --code:#242322; --accent:#a99bff; --warn:#f0a36b; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }}
.wrap {{ max-width:1200px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:2rem; margin:0 0 4px; letter-spacing:-0.02em; }}
.lede {{ color:var(--muted); margin:0 0 20px; max-width:60ch; }}
.stats {{ color:var(--muted); font-size:0.9rem; margin-bottom:16px; }}
.filters {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:24px; }}
.filters button {{ border:1px solid var(--line); background:var(--card); color:var(--fg);
  padding:6px 14px; border-radius:999px; cursor:pointer; font:inherit; }}
.filters button[aria-pressed="true"] {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
.grid {{ display:grid; gap:16px; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); }}
@media (max-width:400px) {{ .grid {{ grid-template-columns:1fr; }} }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:16px; display:flex; flex-direction:column; gap:12px; min-width:0; }}
.card[hidden] {{ display:none; }}
.card header {{ display:flex; gap:6px; align-items:center; flex-wrap:wrap; }}
.card time {{ margin-left:auto; color:var(--muted); font-size:0.8rem; }}
.badge {{ font-size:0.75rem; padding:2px 8px; border-radius:999px; background:var(--code); }}
.badge.task {{ background:var(--accent); color:#fff; }}
.badge.warn {{ color:var(--warn); }}
.badge.model {{ border:1px solid var(--accent); background:transparent; color:var(--accent); }}
h3 {{ font-size:0.8rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--muted);
  margin:0 0 6px; font-weight:600; }}
h3 small {{ text-transform:none; letter-spacing:0; font-weight:400; }}
pre {{ margin:0; background:var(--code); border-radius:8px; padding:10px; overflow:auto;
  max-height:260px; font:12.5px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }}
pre.noise {{ white-space:pre-wrap; word-break:break-all; max-height:120px; }}
pre.prose {{ white-space:pre-wrap; font-family:Georgia,serif; font-size:14px; }}
img.svg {{ display:block; width:100%; height:auto; max-height:360px; object-fit:contain;
  background:#fff; border-radius:8px; border:1px solid var(--line); }}
.card footer {{ display:flex; justify-content:space-between; font-size:0.8rem; color:var(--muted);
  margin-top:auto; }}
a {{ color:var(--accent); }}
.empty {{ color:var(--muted); }}
</style>
</head>
<body>
<div class="wrap">
  <h1>AI Noise</h1>
  <p class="lede">Each card below is one experiment: random noise was handed to an AI as the
  entire request for a program, a piece of writing, or an image. The AI was told which of the
  three to make, and nothing else. Each card names the model that made it.</p>
  <p class="stats">{stats}</p>
  <div class="filters" role="group" aria-label="Filter by task" data-key="task">{filters}</div>
  <div class="filters" role="group" aria-label="Filter by model" data-key="model">{model_filters}</div>
  <main class="grid">{cards}</main>
  <p class="stats">Source and raw results: <a href="https://github.com/{repo}">github.com/{repo}</a></p>
</div>
<script>
const picked = {{ task: 'all', model: 'all' }};
document.querySelectorAll('.filters').forEach(group => {{
  const key = group.dataset.key;
  group.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => {{
    group.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', b === btn));
    picked[key] = btn.dataset.value;
    document.querySelectorAll('.card').forEach(c => c.hidden =
      Object.entries(picked).some(([k, v]) => v !== 'all' && c.dataset[k] !== v));
  }}));
}});
</script>
</body>
</html>
"""


def _filter_buttons(all_label: str, values: list[str]) -> str:
    return f'<button data-value="all" aria-pressed="true">{all_label}</button>' + "".join(
        f'<button data-value="{html.escape(v)}" aria-pressed="false">{html.escape(v)}</button>'
        for v in values
    )


def build_site(runs: list[dict], results_dir: Path, docs_dir: Path, repo: str) -> None:
    runs_dir = docs_dir / "runs"
    if runs_dir.exists():
        shutil.rmtree(runs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    counts = Counter(r["task"] for r in runs)
    models = Counter(_model(r) for r in runs)
    stats = f"{len(runs)} experiments" + "".join(
        f" · {n} {task}" for task, n in sorted(counts.items())
    ) + f" · {len(models)} model{'s' if len(models) != 1 else ''}"
    filters = _filter_buttons("All tasks", sorted(counts))
    model_filters = _filter_buttons("All models", sorted(models))
    cards = "".join(_card(r, results_dir, docs_dir, repo) for r in runs) or (
        '<p class="empty">No experiments yet.</p>'
    )
    (docs_dir / "index.html").write_text(
        PAGE.format(stats=stats, filters=filters, model_filters=model_filters,
                    cards=cards, repo=html.escape(repo)),
        encoding="utf-8",
    )
    (docs_dir / "runs.json").write_text(
        json.dumps(runs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    # Tell GitHub Pages not to run Jekyll over the generated files.
    (docs_dir / ".nojekyll").write_text("", encoding="utf-8")


def build(results_dir: Path | str = "results", docs_dir: Path | str = "docs",
          readme: Path | str | None = "README.md", repo: str | None = None) -> int:
    """Rebuild the site and README table. Returns the number of runs shown."""
    results_dir, docs_dir = Path(results_dir), Path(docs_dir)
    repo = repo or _repo()
    runs = load_runs(results_dir)
    build_site(runs, results_dir, docs_dir, repo)
    if readme is not None and Path(readme).exists():
        update_readme(Path(readme), runs, repo)
    return len(runs)
