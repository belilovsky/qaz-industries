#!/usr/bin/env python3
"""Verify properties of an immutable release artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PAGE_ASSETS = {
    "index.html": ("styles.css", "avds-package-runtime.css", "avds-tokens.css", "avds.css", "runtime.js", "site-shell.js", "locale.js", "app.js", "snapshot-contracts.js", "qazgeo-geometry.js", "qazgeo-map.js", "theme.js"),
    "industry.html": ("styles.css", "avds-package-runtime.css", "avds-tokens.css", "avds.css", "runtime.js", "site-shell.js", "locale.js", "industry-data.js", "snapshot-contracts.js", "profile-view.js", "industry.js", "theme.js"),
    "benchmarks.html": ("styles.css", "avds-package-runtime.css", "avds-tokens.css", "avds.css", "runtime.js", "site-shell.js", "locale.js", "theme.js"),
    "publication.html": ("styles.css", "avds-package-runtime.css", "avds-tokens.css", "avds.css", "runtime.js", "site-shell.js", "locale.js", "theme.js"),
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
    try:
        thematic = json.loads((directory / "data" / "qaz-industries-thematic-release.v1.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"release contract: invalid thematic release: {error}") from error
    if thematic.get("release_id") != args.release or thematic.get("product_id") != "qaz-industries":
        raise SystemExit("release contract: thematic release identity mismatch")
    if not str(thematic.get("manifest_digest", "")).startswith("sha256:"):
        raise SystemExit("release contract: thematic manifest digest missing")
    try:
        avds_coverage = json.loads((directory / "data" / "avds-coverage.v1.json").read_text(encoding="utf-8"))
        avds_system = json.loads((directory / "data" / "avds-system-contract.v1.json").read_text(encoding="utf-8"))
        avds_responsive = json.loads((directory / "data" / "avds-responsive-contract.v1.json").read_text(encoding="utf-8"))
        avds_route_ledger = json.loads((directory / "data" / "avds-route-ledger.v1.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"release contract: invalid AVDS system receipt: {error}") from error
    if avds_coverage.get("system_contract") != "data/avds-system-contract.v1.json" or avds_system.get("schema_version") != "qaz-industries-avds-system-contract-v1":
        raise SystemExit("release contract: AVDS system receipt mismatch")
    if avds_responsive.get("schema_version") != "qaz-industries-avds-responsive-contract-v1" or avds_route_ledger.get("schema_version") != "qaz-industries-avds-route-ledger-v1":
        raise SystemExit("release contract: AVDS responsive or route ledger receipt mismatch")
    map_asset = directory / "data" / "qazgeo-regions-public.v1.geojson"
    if not map_asset.is_file() or map_asset.stat().st_size < 1000:
        raise SystemExit("release contract: QazGeo map asset missing")
    if not (directory / "data" / "ui-locale.v1.json").is_file():
        raise SystemExit("release contract: UI locale catalog missing")
    try:
        portfolio = json.loads((directory / "data" / "portfolio-integration-registry.v1.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"release contract: invalid portfolio integration registry: {error}") from error
    if portfolio.get("schema_version") != "qaz-industries-portfolio-integration-registry-v1" or portfolio.get("product_id") != "qaz-industries":
        raise SystemExit("release contract: portfolio integration registry identity mismatch")
    if len(portfolio.get("integrations", [])) != portfolio.get("measurement", {}).get("scoped_surfaces"):
        raise SystemExit("release contract: portfolio integration registry scope mismatch")
    try:
        consumer = json.loads((directory / "qazstack-consumer.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"release contract: invalid QazStack consumer contract: {error}") from error
    if consumer.get("schema_version") != "qazstack-consumer-contract-v1" or consumer.get("product_id") != "qaz-industries":
        raise SystemExit("release contract: QazStack consumer identity mismatch")
    for discovery_file in ("robots.txt", "sitemap.xml"):
        if not (directory / discovery_file).is_file():
            raise SystemExit(f"release contract: discovery file missing: {discovery_file}")
    version = args.commit[:12]
    for page, assets in PAGE_ASSETS.items():
        source = (directory / page).read_text(encoding="utf-8")
        if f'<meta name="qaz-asset-version" content="{version}" />' not in source:
            raise SystemExit("release contract: industry.html asset version marker missing")
        for asset in assets:
            attribute = "href" if asset.endswith(".css") else "src"
            expected_ref = f'{attribute}="{asset}?v={version}"'
            if expected_ref not in source:
                raise SystemExit(f"release contract: {page} missing {expected_ref}")
    print("release artifact contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
