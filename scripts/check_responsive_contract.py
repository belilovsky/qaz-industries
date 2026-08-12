#!/usr/bin/env python3
"""Validate the declared AVDS responsive model without a browser dependency."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "avds-responsive-contract.v1.json"
EXPECTED_WIDTHS = (320, 390, 768, 820, 1024, 1440, 1920, 2560)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        require(contract.get("schema_version") == "qaz-industries-avds-responsive-contract-v1", "responsive schema")
        viewports = contract.get("viewports")
        require(isinstance(viewports, list) and tuple(item.get("width") for item in viewports) == EXPECTED_WIDTHS, "responsive viewport matrix")
        for item in viewports:
            require(isinstance(item.get("height"), int) and item["height"] > 0, "responsive viewport height")
            require(isinstance(item.get("mode"), str) and item["mode"], "responsive mode")
            require(isinstance(item.get("rule"), str) and item["rule"], "responsive rule")
        recomposition = contract.get("recomposition")
        require(isinstance(recomposition, dict) and set(recomposition) == {"mobile_navigation", "grid", "rails", "line_length", "empty_space"}, "responsive recomposition")
        require(all(isinstance(value, str) and value for value in recomposition.values()), "responsive recomposition copy")
        acceptance = contract.get("acceptance")
        require(acceptance.get("no_horizontal_overflow") is True, "responsive overflow policy")
        require(acceptance.get("all_public_routes") == ["/", "/industry.html", "/benchmarks.html", "/publication.html"], "responsive route set")
        tokens = (ROOT / "avds-tokens.css").read_text(encoding="utf-8")
        styles = (ROOT / "styles.css").read_text(encoding="utf-8")
        components = (ROOT / "avds.css").read_text(encoding="utf-8")
        for token in ("--av-breakpoint-compact", "--av-breakpoint-mobile", "--av-breakpoint-tablet", "--av-breakpoint-desktop", "--av-breakpoint-ultrawide", "--av-container-reading", "--av-container-content", "--av-grid-gutter-compact"):
            require(token in tokens, f"missing responsive token: {token}")
        require("@media (max-width: 720px)" in styles and "@media (max-width: 1100px)" in styles, "responsive CSS breakpoints")
        require("repeat(auto-fit" in styles or "repeat(auto-fit" in components, "responsive auto-fit grid")
        require(".menu-button" in styles and ".mobile-nav" in styles, "responsive navigation")
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"RESPONSIVE CONTRACT FAILED: {error}", file=sys.stderr)
        return 1
    print("responsive contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
