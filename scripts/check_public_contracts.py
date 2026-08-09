#!/usr/bin/env python3
"""Validate public QAZ.INDUSTRIES data contracts without external services."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def https(value: object, label: str) -> None:
    require(isinstance(value, str) and urlparse(value).scheme == "https", f"{label}: HTTPS required")


def main() -> int:
    try:
        profiles = load("industry-profiles.v1.json")
        require(profiles["schema_version"] == "qaz-industries-public-profiles-v1", "profiles schema")
        require(len(profiles["profiles"]) == 4, "expected four industry profiles")
        for profile in profiles["profiles"]:
            require(isinstance(profile.get("id"), str), "profile id")
            https(profile.get("source"), f"profile {profile.get('id')}")
        for entrypoint in profiles["machine_entrypoints"]:
            https(entrypoint.get("url"), "machine entrypoint")

        snapshot = load("qazlake-public-snapshot.v1.json")
        require(snapshot["schema_version"] == "qaz-industries-qazlake-public-snapshot-v1", "snapshot schema")
        require(snapshot["status"] == "ready", "snapshot must state ready")
        retrieved_at = datetime.fromisoformat(snapshot["retrieved_at"].replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - retrieved_at).days
        require(0 <= age_days <= 31, f"snapshot is stale ({age_days} days); refresh before release")
        https(snapshot["provider"]["health_url"], "snapshot health URL")
        https(snapshot["provider"]["endpoint"], "snapshot endpoint")
        require(len(snapshot["indicators"]) == 3, "expected three verified macro indicators")
        for indicator in snapshot["indicators"]:
            require(indicator.get("is_forecast") is False, f"{indicator.get('id')}: forecasts excluded")
            https(indicator.get("source_url"), f"{indicator.get('id')}: source URL")

        registry = load("reviewed-source-registry.v1.json")
        require(registry["schema_version"] == "qazstack-reviewed-source-registry-v1", "registry schema")
        require(registry["source_count"] == len(registry["sources"]), "registry source count")
        require(registry["policy"]["private_materials_are_excluded"] is True, "private exclusion")
        for source in registry["sources"]:
            https(source.get("url"), f"source {source.get('id')}")
            require(source.get("rights_decision") == "approved-link-metadata", f"source {source.get('id')}: rights")

        manifest = json.loads((ROOT / "qazstack-thematic-product.json").read_text(encoding="utf-8"))
        require(manifest["schema_version"] == "qazstack-thematic-product-v1", "thematic manifest schema")
        require(manifest["publication"]["public_records_require_review"] is True, "review gate")
        require(manifest["geo_policy"]["private_browser_access_forbidden"] is True, "private geo browser gate")
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"public contract: FAILED: {error}")
        return 1
    print("public contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
