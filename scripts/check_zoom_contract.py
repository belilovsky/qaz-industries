#!/usr/bin/env python3
"""Validate the recorded 200% zoom/reflow acceptance contract."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
PROOF = ROOT / "data" / "avds-zoom-proof.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        proof = json.loads(PROOF.read_text(encoding="utf-8"))
        require(proof.get("schema_version") == "qaz-industries-avds-zoom-proof-v1", "zoom proof schema")
        require(proof.get("product_id") == "qaz-industries", "zoom proof product")
        require(proof.get("zoom_factor") == 2, "zoom proof must cover 200 percent")
        viewports = proof.get("viewports")
        require(viewports == [320, 390, 768, 1440], "zoom proof viewport matrix")
        routes = proof.get("routes")
        require(isinstance(routes, list) and [item.get("path") for item in routes] == list(PAGES), "zoom proof route matrix")
        require(all(item.get("overflow_free") is True for item in routes), "zoom proof has horizontal overflow")
        require(proof.get("acceptance", {}).get("status") == "verified", "zoom acceptance is not verified")
        require("reflowable" in proof.get("acceptance", {}).get("rule", ""), "zoom acceptance rule")
        for page in PAGES:
            source = (ROOT / page).read_text(encoding="utf-8")
            viewport = re.search(r'<meta\s+name="viewport"\s+content="([^"]+)"', source)
            require(viewport and "user-scalable=no" not in viewport.group(1), f"{page}: browser zoom is restricted")
            require("initial-scale=1" in viewport.group(1), f"{page}: initial viewport scale is missing")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"ZOOM CONTRACT FAILED: {error}", file=sys.stderr)
        return 1
    print("zoom contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
