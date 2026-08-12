#!/usr/bin/env python3
"""Validate that the AVDS route ledger covers every published page and pattern."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "avds-route-ledger.v1.json"
PATH_TO_FILE = {"/": "index.html", "/industry.html": "industry.html", "/benchmarks.html": "benchmarks.html", "/publication.html": "publication.html"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        require(ledger.get("schema_version") == "qaz-industries-avds-route-ledger-v1", "route ledger schema")
        routes = ledger.get("routes")
        require(isinstance(routes, list) and {route.get("path") for route in routes} == set(PATH_TO_FILE), "route ledger route set")
        require(ledger.get("required_viewports") == [320, 390, 768, 820, 1024, 1440, 1920, 2560], "route ledger viewport set")
        for route in routes:
            path = route["path"]
            patterns = route.get("patterns")
            states = route.get("states")
            require(isinstance(patterns, list) and patterns, f"{path}: patterns")
            require(isinstance(states, list) and states, f"{path}: states")
            source = (ROOT / PATH_TO_FILE[path]).read_text(encoding="utf-8")
            for pattern in patterns:
                require(f'data-avds-pattern="{pattern}"' in source, f"{path}: missing pattern {pattern}")
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"AVDS ROUTE LEDGER FAILED: {error}", file=sys.stderr)
        return 1
    print("AVDS route ledger: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
