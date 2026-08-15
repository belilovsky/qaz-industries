#!/usr/bin/env python3
"""Build an immutable, self-contained static QAZ.INDUSTRIES release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = (
    "index.html",
    "industry.html",
    "benchmarks.html",
    "publication.html",
    "styles.css",
    "card-context.css",
    "avds-package-runtime.css",
    "avds-tokens.css",
    "avds.css",
    "runtime.js",
    "site-shell.js",
    "locale.js",
    "snapshot-contracts.js",
    "qazgeo-geometry.js",
    "profile-view.js",
    "app.js",
    "qazgeo-map.js",
    "industry-data.js",
    "industry.js",
    "favicon.svg",
    "theme.js",
    "robots.txt",
    "sitemap.xml",
    "qazstack-thematic-product.json",
    "qazstack-consumer.json",
    "avds-consumer.json",
)
HTML_FILES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
VERSIONED_ASSETS = (
    "styles.css",
    "card-context.css",
    "avds-package-runtime.css",
    "avds-tokens.css",
    "avds.css",
    "runtime.js",
    "site-shell.js",
    "locale.js",
    "snapshot-contracts.js",
    "qazgeo-geometry.js",
    "profile-view.js",
    "app.js",
    "qazgeo-map.js",
    "industry-data.js",
    "industry.js",
    "theme.js",
)


def git_commit() -> str:
    return subprocess.check_output(
        ("git", "rev-parse", "HEAD"), cwd=ROOT, text=True
    ).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if not args.release.replace("-", "").replace("_", "").isalnum():
        raise SystemExit("release identifier must be alphanumeric, '-' or '_'")

    output = args.output or ROOT / ".build" / args.release
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing build: {output}")
    output.mkdir(parents=True)

    commit = git_commit()
    for filename in STATIC_FILES:
        source = ROOT / filename
        if not source.is_file():
            raise SystemExit(f"missing static input: {filename}")
        shutil.copy2(source, output / filename)
    shutil.copytree(ROOT / "data", output / "data")

    # The runtime switches a release symlink atomically. Version local assets in
    # the copied HTML so an already-open browser cannot retain JavaScript or CSS
    # from the prior release after the HTML has moved to the new one.
    asset_version = commit[:12]
    for filename in HTML_FILES:
        destination = output / filename
        html = destination.read_text(encoding="utf-8")
        html = html.replace(
            '<meta name="qaz-asset-version" content="source" />',
            f'<meta name="qaz-asset-version" content="{asset_version}" />',
        )
        for asset in VERSIONED_ASSETS:
            html = html.replace(f'href="{asset}"', f'href="{asset}?v={asset_version}"')
            html = html.replace(f'src="{asset}"', f'src="{asset}?v={asset_version}"')
        destination.write_text(html, encoding="utf-8")

    (output / "release.json").write_text(
        json.dumps(
            {"service": "qaz-industries", "release": args.release, "commit": commit},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    snapshot = json.loads((ROOT / "data" / "qazlake-public-snapshot.v1.json").read_text(encoding="utf-8"))
    territory = json.loads((ROOT / "data" / "qazgeo-public-snapshot.v1.json").read_text(encoding="utf-8"))
    layer_registry = json.loads((ROOT / "data" / "qazgeo-public-layer-registry.v1.json").read_text(encoding="utf-8"))
    manifest_bytes = (ROOT / "qazstack-thematic-product.json").read_bytes()
    published_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    thematic_release = {
        "schema_version": "qazstack-thematic-release-v1",
        "product_id": "qaz-industries",
        "release_id": args.release,
        "published_at": published_at,
        "data_as_of": snapshot["retrieved_at"],
        "manifest_digest": "sha256:" + hashlib.sha256(manifest_bytes).hexdigest(),
        "modules": [
            {"id": "profile-registry", "state": "ready", "record_count": 4, "as_of": published_at, "source_ids": ["qz-energy", "qazaqstan-space", "qaz-farm", "qaz-fish"]},
            {"id": "industry-indicators", "state": "ready", "record_count": 18, "as_of": published_at, "source_ids": ["qz-energy", "qazaqstan-space", "qaz-farm", "qaz-fish"]},
            {"id": "change-pulse", "state": "ready", "record_count": len(snapshot["indicators"]), "as_of": snapshot["retrieved_at"], "source_ids": ["qazlake-macro"]},
            {"id": "source-provenance", "state": "ready", "record_count": 6, "as_of": published_at, "source_ids": ["qz-energy", "qazaqstan-space", "qaz-farm", "qaz-fish", "qazlake-macro", "qazgeo-territory"]},
            {"id": "territorial-context", "state": "ready", "record_count": territory["map_contract"]["feature_count"], "as_of": territory["retrieved_at"], "source_ids": ["qazgeo-territory"], "notes": "20 reviewed QazGeo region geometries plus public layer metadata; QazLake regional values remain unavailable when the documented upstream contract is degraded."},
            {"id": "geo-layer-registry", "state": "ready", "record_count": len(layer_registry["layers"]), "as_of": layer_registry["retrieved_at"], "source_ids": ["qazgeo-territory"], "notes": "Six reviewed QazGeo layer contracts; contract-only hydrology and water catalogues remain metadata-only until upstream observations are available."}
        ],
    }
    (output / "data" / "qaz-industries-thematic-release.v1.json").write_text(
        json.dumps(thematic_release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
