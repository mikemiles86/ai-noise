"""Command line: ``ainoise noise``, ``ainoise run``, ``ainoise build``."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from ainoise import noise as noise_mod
from ainoise.tasks import TASK_NAMES, get_task


def _add_noise_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--strategy", default="random", choices=noise_mod.STRATEGY_NAMES,
                   help="how to make the noise (default: pick one at random)")
    p.add_argument("--length", type=int, default=None,
                   help="characters of noise (default: random, 20-400)")
    p.add_argument("--seed", type=int, default=None,
                   help="seed, to regenerate a previous piece of noise exactly")


def cmd_noise(args: argparse.Namespace) -> int:
    n = noise_mod.generate(args.strategy, args.length, args.seed)
    if args.json:
        print(json.dumps(n.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(n.text)
        print(f"\n[{n.strategy}, {n.length} chars, seed {n.seed}]", file=sys.stderr)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    from ainoise.providers import get_provider
    from ainoise.runner import run_experiment
    from ainoise.showcase import build

    tasks = TASK_NAMES if args.task == "all" else [args.task]
    provider = None
    if not args.dry_run:
        kwargs = {}
        if args.provider == "claude":
            kwargs = {"model": args.model, "effort": args.effort}
        provider = get_provider(args.provider, **kwargs)

    for i in range(args.count):
        seed = args.seed if (args.seed is not None and i == 0) else None
        n = noise_mod.generate(args.strategy, args.length, seed)
        started = datetime.now(timezone.utc)
        # With --task all, the same noise goes to every task, so the three
        # results can be compared side by side.
        for task in tasks:
            if args.dry_run:
                print(f"--- {task} ---\nSYSTEM: {get_task(task).system_prompt}\n"
                      f"USER ({n.strategy}, seed {n.seed}):\n{n.text}\n")
                continue
            run_dir = run_experiment(task, n, provider, args.results_dir, now=started)
            record = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            print(f"{run_dir}  [{record['stop_reason']}, {record['artifact']['kind']}]")

    if not args.dry_run and not args.no_build:
        count = build(args.results_dir, args.docs_dir, args.readme)
        print(f"showcase rebuilt: {count} runs")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    from ainoise.showcase import build

    count = build(args.results_dir, args.docs_dir, args.readme)
    print(f"showcase rebuilt: {count} runs")
    return 0


def parser() -> argparse.ArgumentParser:
    from ainoise.providers import DEFAULT_EFFORT, DEFAULT_MODEL

    p = argparse.ArgumentParser(prog="ainoise", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    pn = sub.add_parser("noise", help="print a piece of random text")
    _add_noise_args(pn)
    pn.add_argument("--json", action="store_true", help="print strategy, length and seed too")
    pn.set_defaults(func=cmd_noise)

    pr = sub.add_parser("run", help="feed noise to the AI as a task and record the result")
    pr.add_argument("--task", required=True, choices=TASK_NAMES + ["all"])
    _add_noise_args(pr)
    pr.add_argument("--count", type=int, default=1, help="how many experiments (fresh noise each)")
    pr.add_argument("--provider", default="claude", choices=["claude", "mock"])
    pr.add_argument("--model", default=DEFAULT_MODEL)
    pr.add_argument("--effort", default=DEFAULT_EFFORT,
                    choices=["low", "medium", "high", "xhigh", "max"])
    pr.add_argument("--dry-run", action="store_true",
                    help="print the prompts without calling the AI or saving anything")
    pr.add_argument("--no-build", action="store_true", help="skip rebuilding the showcase")
    _add_paths(pr)
    pr.set_defaults(func=cmd_run)

    pb = sub.add_parser("build", help="rebuild docs/ and the README table from results/")
    _add_paths(pb)
    pb.set_defaults(func=cmd_build)
    return p


def _add_paths(p: argparse.ArgumentParser) -> None:
    p.add_argument("--results-dir", default="results")
    p.add_argument("--docs-dir", default="docs")
    p.add_argument("--readme", default="README.md")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args)
