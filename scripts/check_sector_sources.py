#!/usr/bin/env python3
"""Read-only drift probe for the four public sector products used by QAZ."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data" / "industry-profiles.v1.json"
INDUSTRY_DATA = ROOT / "industry-data.js"
USER_AGENT = "QAZ.INDUSTRIES-sector-monitor/1.0"


def fetch(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"HTTPS URL required: {url}")
    return subprocess.run(
        (
            "curl", "--fail", "--silent", "--show-error", "--location",
            "--retry", "2", "--retry-all-errors", "--retry-delay", "1",
            "--connect-timeout", "10", "--max-time", "40",
            "--user-agent", USER_AGENT, url,
        ),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def probe(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"HTTPS URL required: {url}")
    subprocess.run(
        (
            "curl", "--fail", "--silent", "--show-error", "--location",
            "--retry", "2", "--retry-all-errors", "--retry-delay", "1",
            "--connect-timeout", "10", "--max-time", "40",
            "--user-agent", USER_AGENT, "--output", "/dev/null", url,
        ),
        check=True,
    )


def fetch_json(url: str) -> dict:
    payload = json.loads(fetch(url))
    if not isinstance(payload, dict):
        raise ValueError(f"{url}: JSON object required")
    return payload


def require_release(local_release_id: str, upstream_release: object, profile_id: str) -> str:
    if not isinstance(upstream_release, str) or not upstream_release:
        raise ValueError(f"{profile_id}: upstream release id is missing")
    if upstream_release != local_release_id:
        raise ValueError(f"{profile_id}: local source release differs from upstream {upstream_release}")
    return upstream_release


def selected_count(payload: dict, module_id: str) -> int:
    modules = payload.get("modules")
    if not isinstance(modules, list):
        raise ValueError("thematic release modules are missing")
    module = next((item for item in modules if isinstance(item, dict) and item.get("id") == module_id), None)
    if not isinstance(module, dict) or not isinstance(module.get("record_count"), int):
        raise ValueError(f"thematic release module is missing: {module_id}")
    return module["record_count"]


def indexed_count(payload: dict, file_id: str) -> int:
    files = payload.get("files")
    if not isinstance(files, list):
        raise ValueError("public data index files are missing")
    item = next(
        (entry for entry in files if isinstance(entry, dict) and entry.get("id") == file_id),
        None,
    )
    if not isinstance(item, dict) or not isinstance(item.get("count"), int):
        raise ValueError(f"public data index entry is missing: {file_id}")
    return item["count"]


def main() -> int:
    registry = json.loads(PROFILES.read_text(encoding="utf-8"))
    profiles = {item["id"]: item for item in registry["profiles"]}

    energy = fetch_json("https://qz.energy/data/thematic-release.json")
    farm = fetch_json("https://qaz.farm/thematic-release.json")
    water = fetch_json("https://qaz.fish/data/thematic-release.json")
    space = fetch_json("https://qazaqstan.space/data/v1/index.json")

    report = {
        "schema_version": "qaz-industries-sector-source-probe-v1",
        "profiles": {
            "energy": {
                "release": require_release(profiles["energy"]["source_release_id"], energy.get("release_id"), "energy"),
                "indicators": selected_count(energy, "energy-indicators"),
                "objects": selected_count(energy, "system-map"),
                "sources": selected_count(energy, "source-register"),
            },
            "space": {
                "release": require_release(profiles["space"]["source_release_id"], space.get("release_id"), "space"),
                "objects": indexed_count(space, "entities"),
                "facts": indexed_count(space, "claims"),
                "sources": indexed_count(space, "sources"),
            },
            "farm": {
                "release": require_release(profiles["farm"]["source_release_id"], farm.get("release_id"), "farm"),
                "sources": selected_count(farm, "source-status"),
                "entities": selected_count(farm, "entity-registry"),
            },
            "water": {
                "release": require_release(profiles["water"]["source_release_id"], water.get("release_id"), "water"),
                "water_objects": selected_count(water, "water-explorer"),
                "lessons": selected_count(water, "fishing-academy"),
            },
        },
    }

    source_urls = sorted(set(re.findall(r"https://[^']+", INDUSTRY_DATA.read_text(encoding="utf-8"))))
    for url in source_urls:
        probe(url)
    report["source_links_checked"] = len(source_urls)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
