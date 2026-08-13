#!/usr/bin/env python3
"""Dependency-free integrity checks for the static QAZ.INDUSTRIES surface."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
STYLE_ORDER = ("styles.css", "avds-package-runtime.css", "avds-tokens.css", "avds.css")
SCRIPT_ORDER = {
    "index.html": ("runtime.js", "site-shell.js", "locale.js", "app.js", "snapshot-contracts.js", "qazgeo-geometry.js", "qazgeo-map.js"),
    "industry.html": ("runtime.js", "site-shell.js", "locale.js", "industry-data.js", "snapshot-contracts.js", "profile-view.js", "industry.js"),
    "benchmarks.html": ("runtime.js", "site-shell.js", "locale.js"),
    "publication.html": ("runtime.js", "site-shell.js", "locale.js"),
}
ASSETS = (
    "styles.css",
    "avds-package-runtime.css",
    "avds-tokens.css",
    "avds.css",
    "runtime.js",
    "site-shell.js",
    "snapshot-contracts.js",
    "qazgeo-geometry.js",
    "profile-view.js",
    "app.js",
    "qazgeo-map.js",
    "industry-data.js",
    "industry.js",
    "favicon.svg",
    "theme.js",
    "locale.js",
    "robots.txt",
    "sitemap.xml",
    "qazstack-consumer.json",
    "data/avds-coverage.v1.json",
    "data/avds-system-contract.v1.json",
    "data/avds-responsive-contract.v1.json",
    "data/avds-route-ledger.v1.json",
    "data/avds-icon-catalog.v1.json",
    "data/avds-data-visualization-contract.v1.json",
    "data/avds-accessibility-contract.v1.json",
    "data/avds-zoom-proof.v1.json",
    "data/avds-visual-regression.v1.json",
    "data/ui-locale.v1.json",
    "content/locale-contract.v1.json",
    "avds-consumer.json",
)


class HTMLCheck(HTMLParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        coverage = json.loads((ROOT / "data" / "avds-coverage.v1.json").read_text(encoding="utf-8"))
        version = coverage["avds"]["version"]
        badge = coverage["badge"]
        route_percent = coverage["route_contract"]["coverage_percent"]
        for asset in ASSETS:
            require((ROOT / asset).is_file(), f"missing asset: {asset}")

        for page in PAGES:
            source = (ROOT / page).read_text(encoding="utf-8")
            parser = HTMLCheck()
            parser.feed(source)
            parser.close()
            require('data-design-system="avds4"' in source, f"{page}: missing AV DS root marker")
            require('data-av-theme="institutional"' in source, f"{page}: missing AV DS theme")
            style_positions = [source.index(f'href="{stylesheet}"') for stylesheet in STYLE_ORDER]
            require(style_positions == sorted(style_positions), f"{page}: AV DS styles are out of dependency order")
            require('data-theme-toggle' in source, f"{page}: missing AV DS theme control")
            require('src="locale.js"' in source, f"{page}: missing locale runtime")
            require('src="theme.js"' in source, f"{page}: missing external theme bootstrap")
            require('src="runtime.js"' in source, f"{page}: missing shared browser runtime")
            script_positions = [source.index(f'src="{script}"') for script in SCRIPT_ORDER[page]]
            require(script_positions == sorted(script_positions), f"{page}: shared scripts are out of dependency order")
            require('<meta name="qaz-asset-version" content="source" />' in source, f"{page}: missing asset version marker")
            require('rel="canonical"' in source, f"{page}: missing canonical URL")
            require('property="og:title"' in source and 'property="og:description"' in source, f"{page}: missing OpenGraph metadata")
            require('data-avds-coverage-badge' in source, f"{page}: missing AVDS coverage badge")
            require(badge in source, f"{page}: stale AVDS coverage badge")
            require(f"базовый маршрутный контракт: {route_percent} процентов" in source, f"{page}: stale AVDS route coverage label")
            require('data-avds-pattern="app-shell"' in source, f"{page}: missing AVDS app shell")
            require('data-avds-pattern="site-footer"' in source, f"{page}: missing AVDS site footer")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        avds = (ROOT / "avds.css").read_text(encoding="utf-8")
        require(
            'html[data-design-system="avds4"] [hidden]' in avds
            and ("display: none !important" in avds or "display:none !important" in avds),
            "avds.css: native hidden contract must override component display modes",
        )
        require('id="filter-summary"' in index, "index.html: missing filter status")
        require(index.count('data-qazgeo-map') == 2, "index.html: expected hero and full QazGeo maps")
        require('src="qazgeo-map.js"' in index, "index.html: missing QazGeo renderer")
        require('data-map-svg' in index and 'data/qazgeo-regions-public.v1.geojson' in index, "index.html: missing QazGeo map contract")
        require(index.count('av-card') >= 14, "index.html: shared surfaces missing AV DS cards")
        profile = (ROOT / "industry.html").read_text(encoding="utf-8")
        for element_id in (
            "profile-evidence-source", "profile-evidence-release", "profile-evidence-link",
            "profile-passport-title", "passport-source", "passport-release", "profile-machine-link",
            "public-export-title", "pulse-status", "pulse-grid", "territory-status", "territory-grid", "pulse-boundary-state",
            "layer-registry-status", "layer-registry-grid",
            "questions", "source-links",
        ):
            require(f'id="{element_id}"' in profile, f"industry.html: missing {element_id}")
        require('class="indicator-table av-table"' in profile and 'class="compare-table av-table"' in profile, "industry.html: missing AV DS table contracts")
        require('data-avds-pattern="public-export-matrix"' in profile, "industry.html: missing AV DS public export pattern")
        require('data-avds-pattern="evidence-source-registry"' in profile, "industry.html: missing AV DS source registry pattern")
        require('data-avds-pattern="geo-layer-registry"' in profile, "industry.html: missing AV DS geo layer registry pattern")
        require('data-avds-pattern="related-question-grid"' in profile, "industry.html: missing AV DS question pattern")
        require('src="locale.js"' in profile, "industry.html: missing locale contract runtime")
        profile_view = (ROOT / "profile-view.js").read_text(encoding="utf-8")
        require(profile_view.count("av-card av-card--outlined") >= 5, "profile-view.js: dynamic surfaces missing AV DS card contracts")
        require("av-source-registry__metadata" in profile_view, "profile-view.js: source registry metadata missing")
        require("av-layer-registry__metadata" in profile_view, "profile-view.js: geo layer registry metadata missing")
        benchmark = (ROOT / "benchmarks.html").read_text(encoding="utf-8")
        for contract in ("av-chip", "av-card", "av-table", "av-button"):
            require(contract in benchmark, f"benchmarks.html: missing AV DS contract {contract}")
        for contract in (
            "qazstack-consumer.json",
            "data/industry-profiles.v1.json",
            "data/qazlake-public-snapshot.v1.json",
            "data/qazgeo-public-snapshot.v1.json",
            "data/qazgeo-regions-public.v1.geojson",
            "data/qazgeo-public-layer-registry.v1.json",
            "data/reviewed-source-registry.v1.json",
            "data/portfolio-integration-registry.v1.json",
            "data/qaz-industries-thematic-release.v1.json",
        ):
            require((ROOT / contract).is_file(), f"missing public contract: {contract}")

        styles = (ROOT / "styles.css").read_text(encoding="utf-8")
        require("@import" not in styles and "fonts.googleapis.com" not in styles, "styles.css: external font import remains")
        css = (ROOT / "avds.css").read_text(encoding="utf-8")
        tokens = (ROOT / "avds-tokens.css").read_text(encoding="utf-8")
        require(css.count("{") == css.count("}"), "avds.css: unbalanced braces")
        require(tokens.count("{") == tokens.count("}"), "avds-tokens.css: unbalanced braces")
        require("--av-color-primary:" not in css, "avds.css: design tokens leaked into component layer")
        for token in ("--av-spacing-4", "--av-radius-lg", "--av-color-primary", "data-av-theme=\"golden-paper\""):
            require(token in tokens, f"avds-tokens.css: missing token {token}")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"CHECK FAILED: {error}", file=sys.stderr)
        return 1

    print("static contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
