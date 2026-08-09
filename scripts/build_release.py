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
HTML_FILES = ("index.html", "industry.html", "benchmarks.html")
VERSIONED_ASSETS = ("styles.css", "avds.css", "app.js", "industry-data.js", "industry.js")


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

    commit = git_commit()
    for filename in STATIC_FILES:
        source = ROOT / filename
        if not source.is_file():
            raise SystemExit(f"missing static input: {filename}")
        shutil.copy2(source, output / filename)

    # The runtime switches a release symlink atomically. Version local assets in
    # the copied HTML so an already-open browser cannot retain JavaScript or CSS
    # from the prior release after the HTML has moved to the new one.
    asset_version = commit[:12]
    for filename in HTML_FILES:
        destination = output / filename
        html = destination.read_text(encoding="utf-8")
        for asset in VERSIONED_ASSETS:
            html = html.replace(f'href="{asset}"', f'href="{asset}?v={asset_version}"')
            html = html.replace(f'src="{asset}"', f'src="{asset}?v={asset_version}"')
        destination.write_text(html, encoding="utf-8")

    (output / "release.json").write_text(
        json.dumps(
            {"service": "qaz-industries", "release": args.release, "commit": commit},
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
