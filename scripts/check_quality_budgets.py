#!/usr/bin/env python3
"""Fail closed on frontend size drift and release/security contract regressions."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
CSS_FILES = ("styles.css", "avds-tokens.css", "avds.css")
PUBLIC_DATA = (
    "industry-profiles.v1.json",
    "qazlake-public-snapshot.v1.json",
    "qazgeo-public-snapshot.v1.json",
    "qazgeo-public-layer-registry.v1.json",
    "qazgeo-regions-public.v1.geojson",
    "reviewed-source-registry.v1.json",
)
SENSITIVE_KEYS = {"password", "secret", "access_token", "refresh_token", "email", "phone", "user_id", "private_id"}


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[dict[str, str]] = []
        self.styles: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "script" and attributes.get("src"):
            self.scripts.append(attributes)
        if tag == "link" and attributes.get("rel") == "stylesheet":
            self.styles.append(attributes.get("href", ""))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def byte_total(paths: list[Path]) -> int:
    return sum(path.stat().st_size for path in paths)


def walk_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).casefold())
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


def main() -> int:
    try:
        html_paths = [ROOT / page for page in PAGES]
        css_paths = [ROOT / name for name in CSS_FILES]
        js_paths = sorted(ROOT.glob("*.js"))
        data_paths = [ROOT / "data" / name for name in PUBLIC_DATA]
        require(byte_total(html_paths) <= 96 * 1024, "HTML budget exceeded (96 KiB)")
        require(byte_total(css_paths) <= 96 * 1024, "CSS budget exceeded (96 KiB)")
        require(byte_total(js_paths) <= 96 * 1024, "JavaScript budget exceeded (96 KiB)")
        require(byte_total(data_paths) <= 512 * 1024, "public data budget exceeded (512 KiB)")
        require((ROOT / "data" / "qazgeo-regions-public.v1.geojson").stat().st_size <= 450 * 1024, "QazGeo map budget exceeded (450 KiB)")
        require((ROOT / "theme.js").stat().st_size <= 2 * 1024, "synchronous theme bootstrap exceeds 2 KiB")
        require(all(path.stat().st_size <= 24 * 1024 for path in js_paths), "single JavaScript module exceeds 24 KiB")

        for page in PAGES:
            parser = AssetParser()
            parser.feed((ROOT / page).read_text(encoding="utf-8"))
            parser.close()
            require(parser.styles == list(CSS_FILES), f"{page}: unexpected stylesheet order or count")
            blocking = [script["src"] for script in parser.scripts if "defer" not in script]
            require(blocking == ["theme.js"], f"{page}: only theme.js may block parsing")

        caddy = (ROOT / "deploy" / "qaz-industries.caddy.fragment").read_text(encoding="utf-8")
        for directive in (
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "Referrer-Policy",
            "X-Frame-Options",
            "Permissions-Policy",
            "Content-Security-Policy",
            "Cross-Origin-Opener-Policy",
            "Cross-Origin-Resource-Policy",
            "X-Qaz-Industries-Release",
        ):
            require(directive in caddy, f"Caddy security contract missing {directive}")
        csp = next(line for line in caddy.splitlines() if "Content-Security-Policy" in line)
        require("'unsafe-inline'" not in csp and "'unsafe-eval'" not in csp and " *" not in csp, "CSP contains an unsafe source")
        require("connect-src 'self'" in csp and "form-action 'self'" in csp, "CSP browser boundaries are incomplete")
        require("@hidden path /.env /.git/*" in caddy, "sensitive path denylist is missing")

        deploy = (ROOT / "scripts" / "deploy.sh").read_text(encoding="utf-8")
        require("Refusing to deploy a dirty worktree" in deploy, "deploy dirty-worktree guard is missing")
        require("BatchMode=yes" in deploy, "deploy SSH must be non-interactive")
        require("caddy validate" in deploy and "rollback()" in deploy, "deploy validation or rollback guard is missing")

        for path in data_paths:
            payload = json.loads(path.read_text(encoding="utf-8"))
            exposed = walk_keys(payload) & SENSITIVE_KEYS
            require(not exposed, f"{path.name}: sensitive keys exposed: {sorted(exposed)}")
        consumer_path = ROOT / "qazstack-consumer.json"
        consumer = json.loads(consumer_path.read_text(encoding="utf-8"))
        exposed = walk_keys(consumer) & SENSITIVE_KEYS
        require(not exposed, f"{consumer_path.name}: sensitive keys exposed: {sorted(exposed)}")
    except (OSError, StopIteration, ValueError, json.JSONDecodeError) as error:
        print(f"QUALITY BUDGET FAILED: {error}", file=sys.stderr)
        return 1
    print("quality budgets: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
