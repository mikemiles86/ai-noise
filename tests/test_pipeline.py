import json
from datetime import datetime, timezone

from ainoise.cli import main
from ainoise.noise import generate
from ainoise.providers import MockProvider
from ainoise.runner import load_runs, run_experiment
from ainoise.showcase import README_END, README_START, build
from ainoise.tasks import get_task

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)


def test_extractors():
    code = get_task("code").extract("Here:\n```python\nprint(1)\n```\nDone.")
    assert (code.filename, code.content, code.language) == ("output.py", "print(1)\n", "python")
    svg = get_task("image").extract('<svg viewBox="0 0 1 1"></svg> A dot.')
    assert svg.kind == "svg" and 'xmlns="http://www.w3.org/2000/svg"' in svg.content
    assert get_task("image").extract("no image, sorry").kind == "raw"
    assert get_task("code").extract("no fence").kind == "raw"


def test_run_records_everything(tmp_path):
    n = generate("keysmash", 80, seed=9)
    run_dir = run_experiment("image", n, MockProvider(), tmp_path, now=NOW)
    record = json.loads((run_dir / "run.json").read_text())
    assert record["noise"]["seed"] == 9
    assert record["prompt"]["user"] == n.text
    assert record["artifact"]["file"] == "output.svg"
    assert (run_dir / "output.svg").exists() and (run_dir / "response.md").exists()
    assert load_runs(tmp_path)[0]["id"] == run_dir.name


def test_showcase_escapes_and_updates_readme(tmp_path):
    results, docs = tmp_path / "results", tmp_path / "docs"
    readme = tmp_path / "README.md"
    readme.write_text(f"# Hi\n{README_START}\nold\n{README_END}\nbye\n")
    n = generate("chars", 40, seed=3)
    object.__setattr__(n, "text", "<script>alert(1)</script> | pipe")
    for task in ("code", "text", "image"):
        run_experiment(task, n, MockProvider(), results, now=NOW)

    assert build(results, docs, readme, repo="me/repo") == 3
    page = (docs / "index.html").read_text()
    assert "<script>alert(1)" not in page and "&lt;script&gt;" in page
    assert page.count('class="card"') == 3
    assert len(json.loads((docs / "runs.json").read_text())) == 3
    assert list((docs / "runs").glob("*/output.svg"))
    text = readme.read_text()
    assert "old" not in text and text.endswith("bye\n")
    assert "&#124; pipe" in text and "github.com/me/repo/tree/main/results/" in text


def test_cli_end_to_end(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text(f"{README_START}\n{README_END}\n")
    args = ["--results-dir", str(tmp_path / "r"), "--docs-dir", str(tmp_path / "d"),
            "--readme", str(readme)]
    assert main(["run", "--task", "all", "--provider", "mock", "--seed", "5", *args]) == 0
    runs = load_runs(tmp_path / "r")
    assert sorted(r["task"] for r in runs) == ["code", "image", "text"]
    assert len({r["noise"]["text"] for r in runs}) == 1  # same noise for all three
    assert "showcase rebuilt: 3 runs" in capsys.readouterr().out
    assert main(["run", "--task", "code", "--dry-run", "--seed", "1"]) == 0
    assert main(["noise", "--strategy", "syllables", "--length", "30", "--seed", "1"]) == 0
