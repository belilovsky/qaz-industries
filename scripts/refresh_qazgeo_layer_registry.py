#!/usr/bin/env python3
"""Fetch a reviewed, metadata-only registry of public QazGeo layers.

The registry deliberately excludes layer features and raw observations.  It
is a small, immutable release input which makes available contracts visible
without turning a contract-only upstream into a fabricated data source.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urljoin

try:
    from .public_snapshot import emit_snapshot, fetch_json, utc_timestamp
except ImportError:
    from public_snapshot import emit_snapshot, fetch_json, utc_timestamp


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "qazgeo-public-layer-registry.v1.json"
HEALTH_URL = "https://qgeo.tech/health/ready"
LAYERS_URL = "https://qgeo.tech/api/v1/layers"
BASE_URL = "https://qgeo.tech"
SELECTED_LAYER_IDS = (
    "regions",
    "infrastructure",
    "national_transport_network",
    "national_place_nodes",
    "hydro_stations",
    "water_objects_catalog",
)


def safe_coverage(value: object) -> dict:
    if not isinstance(value, dict):
        return {}
    return {key: value[key] for key in ("scope", "status", "geographies", "segments", "features", "geometry") if key in value}


def sanitize_layer(layer: dict) -> dict:
    layer_id = layer.get("id")
    if layer_id not in SELECTED_LAYER_IDS:
        raise ValueError(f"unexpected selected layer: {layer_id}")
    if layer.get("status") not in {"stable", "beta"}:
        raise ValueError(f"{layer_id}: unsupported layer status")
    if layer.get("public_allowed") is not True:
        raise ValueError(f"{layer_id}: public layer must be explicitly allowed")

    governance = layer.get("governance")
    provenance = layer.get("provenance")
    if not isinstance(governance, dict) or not isinstance(provenance, dict):
        raise ValueError(f"{layer_id}: governance and provenance are required")
    contract_path = governance.get("contract_path") or layer.get("endpoint") or layer.get("tilejson")
    if not isinstance(contract_path, str) or not contract_path.startswith("/"):
        raise ValueError(f"{layer_id}: public contract path is missing")
    source_url = governance.get("source_url") or LAYERS_URL
    if not isinstance(source_url, str) or not source_url.startswith("https://"):
        raise ValueError(f"{layer_id}: reviewed source URL must be HTTPS")
    dataset_status = governance.get("dataset_status") or layer.get("observation_status")
    if dataset_status not in {"versioned_snapshot", "observed_snapshot", "contract_only"}:
        raise ValueError(f"{layer_id}: unsupported dataset status {dataset_status}")
    projection = governance.get("public_projection")
    if not isinstance(projection, list) or not all(isinstance(item, str) for item in projection):
        raise ValueError(f"{layer_id}: public projection must be a list of field names")

    return {
        "id": layer_id,
        "title": layer.get("title") or layer_id,
        "description": layer.get("description") or "",
        "kind": layer.get("kind") or "unknown",
        "status": layer["status"],
        "public_allowed": True,
        "contract": governance.get("contract") or "qazgeo-layer/v1",
        "dataset_status": dataset_status,
        "contract_url": urljoin(BASE_URL, contract_path),
        "source_url": source_url,
        "provenance": {
            "label": provenance.get("label") or layer_id,
            "attribution": provenance.get("attribution") or "QazGeo",
        },
        "license": {
            "status": governance.get("license_status") or "reviewed",
            "note": governance.get("license_note") or "Публичный слой с ограничениями, подтверждёнными проверкой.",
        },
        "coverage": safe_coverage(governance.get("coverage")),
        "public_projection": projection,
        "freshness": {
            "data_updated_at": governance.get("data_updated_at"),
            "schema_updated_at": governance.get("schema_updated_at"),
            "observed_at": governance.get("observed_at"),
            "refresh_slo_seconds": governance.get("refresh_slo_seconds"),
        },
        "limitations": governance.get("limitations") or "Публичный контракт требует отдельной проверки перед использованием.",
    }


def snapshot() -> dict:
    health = fetch_json(HEALTH_URL)
    if health.get("status") != "ok" or health.get("service") != "qazgeo":
        raise ValueError("QazGeo health contract is not ready")
    source_revision = health.get("source_revision")
    if not isinstance(source_revision, str) or not source_revision:
        raise ValueError("QazGeo health response is missing source revision")

    payload = fetch_json(LAYERS_URL)
    layers = payload.get("layers")
    if not isinstance(layers, list):
        raise ValueError("QazGeo layer registry is not a list")
    by_id = {item.get("id"): item for item in layers if isinstance(item, dict)}
    selected = [sanitize_layer(by_id[layer_id]) for layer_id in SELECTED_LAYER_IDS if layer_id in by_id]
    if len(selected) != len(SELECTED_LAYER_IDS):
        missing = sorted(set(SELECTED_LAYER_IDS) - {item["id"] for item in selected})
        raise ValueError(f"QazGeo selected layers are missing: {', '.join(missing)}")

    return {
        "schema_version": "qaz-industries-qazgeo-public-layer-registry-v1",
        "status": "ready",
        "provider": {
            "service": health["service"],
            "source_revision": source_revision,
            "health_url": HEALTH_URL,
            "layer_registry_url": LAYERS_URL,
        },
        "retrieved_at": utc_timestamp(),
        "publication_mode": "reviewed-static-metadata",
        "layers": selected,
        "limitations": [
            "Это проверенный реестр контрактов QazGeo, а не выгрузка объектов или наблюдений.",
            "Слои со статусом «contract_only» показываются как план подключения: значения, координаты и оперативные наблюдения не публикуются до отдельной проверки исходного источника.",
            "OSM-слои требуют атрибуции и не заменяют официальные инженерные, дорожные или гидрологические реестры.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="replace the checked-in registry after review")
    args = parser.parse_args()
    result = snapshot()
    emit_snapshot(result, OUTPUT, write=args.write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
