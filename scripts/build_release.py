#!/usr/bin/env python3
"""Build an immutable, self-contained static QAZ.INDUSTRIES release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = (
    "index.html",
    "industry.html",
    "benchmarks.html",
    "styles.css",
    "avds.css",
    "app.js",
    "industry-data.js",
    "industry.js",
    "favicon.svg",
)


def git_commit() -> str:
    return subprocess.check_output(
        ("git", "rev-parse", "HEAD"), cwd=ROOT, text=True
    ).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if not args.release.replace("-", "").replace("_", "").isalnum():
        raise SystemExit("release identifier must be alphanumeric, '-' or '_'")

    output = args.output or ROOT / ".build" / args.release
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing build: {output}")
    output.mkdir(parents=True)

    for filename in STATIC_FILES:
        source = ROOT / filename
        if not source.is_file():
            raise SystemExit(f"missing static input: {filename}")
        shutil.copy2(source, output / filename)

    (output / "release.json").write_text(
        json.dumps(
            {"service": "qaz-industries", "release": args.release, "commit": git_commit()},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
