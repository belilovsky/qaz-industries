#!/usr/bin/env python3
"""Validate the complete inline icon API used by the public QAZ surface."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "avds-icon-catalog.v1.json"
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        require(catalog.get("schema_version") == "qaz-industries-avds-icon-catalog-v1", "icon catalog schema")
        policy = catalog.get("policy") or {}
        require(policy.get("external_font_files") is False and policy.get("license"), "icon catalog licensing policy")
        icons = catalog.get("icons")
        require(isinstance(icons, list) and len(icons) >= 7, "icon catalog must cover every public glyph")
        names = [icon.get("name") for icon in icons]
        require(len(names) == len(set(names)) and all(isinstance(name, str) and name for name in names), "icon names")
        surface = "\n".join((ROOT / page).read_text(encoding="utf-8") for page in PAGES)
        surface += (ROOT / "styles.css").read_text(encoding="utf-8")
        for icon in icons:
            require(icon.get("marker") in surface, f"icon marker missing: {icon.get('name')}")
            require(icon.get("size") and icon.get("weight"), f"icon dimensions missing: {icon.get('name')}")
        require(".av-icon" in (ROOT / "avds.css").read_text(encoding="utf-8"), "icon component API missing")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"ICON CATALOG FAILED: {error}", file=sys.stderr)
        return 1
    print("icon catalog: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
