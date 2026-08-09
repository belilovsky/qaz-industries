#!/usr/bin/env python3
"""Dependency-free integrity checks for the static QAZ.INDUSTRIES surface."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "industry.html", "benchmarks.html")
ASSETS = (
    "styles.css",
    "avds.css",
    "app.js",
    "industry-data.js",
    "industry.js",
    "favicon.svg",
)


class HTMLCheck(HTMLParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        for asset in ASSETS:
            require((ROOT / asset).is_file(), f"missing asset: {asset}")

        for page in PAGES:
            source = (ROOT / page).read_text(encoding="utf-8")
            parser = HTMLCheck()
            parser.feed(source)
            parser.close()
            require('data-design-system="avds4"' in source, f"{page}: missing AV DS root marker")
            require('data-av-theme="institutional"' in source, f"{page}: missing AV DS theme")
            require('href="avds.css"' in source, f"{page}: missing AV DS stylesheet")
            require('data-theme-toggle' in source, f"{page}: missing AV DS theme control")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        require('id="filter-summary"' in index, "index.html: missing filter status")
        profile = (ROOT / "industry.html").read_text(encoding="utf-8")
        for element_id in (
            "profile-evidence-source", "profile-evidence-release", "profile-evidence-link",
            "profile-passport-title", "passport-source", "passport-release", "profile-machine-link",
            "public-export-title", "pulse-status", "pulse-grid", "territory-status", "territory-grid", "pulse-boundary-state",
            "questions",
        ):
            require(f'id="{element_id}"' in profile, f"industry.html: missing {element_id}")
        require('window.QAZ_INDUSTRIES_ASSET_VERSION = "source"' in profile, "industry.html: missing asset version bootstrap")
        for contract in (
            "data/industry-profiles.v1.json",
            "data/qazlake-public-snapshot.v1.json",
            "data/qazgeo-public-snapshot.v1.json",
            "data/reviewed-source-registry.v1.json",
            "data/qaz-industries-thematic-release.v1.json",
        ):
            require((ROOT / contract).is_file(), f"missing public contract: {contract}")

        css = (ROOT / "avds.css").read_text(encoding="utf-8")
        require(css.count("{") == css.count("}"), "avds.css: unbalanced braces")
        for token in ("--av-spacing-4", "--av-radius-lg", "--av-color-primary", "data-av-theme=\"golden-paper\""):
            require(token in css, f"avds.css: missing token {token}")
    except (OSError, ValueError) as error:
        print(f"CHECK FAILED: {error}", file=sys.stderr)
        return 1

    print("static contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
