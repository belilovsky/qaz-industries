#!/usr/bin/env python3
"""Verify properties of an immutable release artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PAGE_ASSETS = {
    "index.html": ("styles.css", "avds.css", "app.js"),
    "industry.html": ("styles.css", "avds.css", "app.js", "industry-data.js", "industry.js"),
    "benchmarks.html": ("styles.css", "avds.css", "app.js"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()

    directory = args.directory
    if not directory.is_dir():
        raise SystemExit(f"release contract: missing directory: {directory}")
    try:
        metadata = json.loads((directory / "release.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"release contract: invalid release.json: {error}") from error
    expected = {"service": "qaz-industries", "release": args.release, "commit": args.commit}
    if metadata != expected:
        raise SystemExit(f"release contract: unexpected metadata: {metadata!r}")
    version = args.commit[:12]
    for page, assets in PAGE_ASSETS.items():
        source = (directory / page).read_text(encoding="utf-8")
        for asset in assets:
            attribute = "href" if asset.endswith(".css") else "src"
            expected_ref = f'{attribute}="{asset}?v={version}"'
            if expected_ref not in source:
                raise SystemExit(f"release contract: {page} missing {expected_ref}")
    print("release artifact contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
