#!/usr/bin/env python3
"""Fetch the narrow public QazGeo territory snapshot for reviewed static use."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "qazgeo-public-snapshot.v1.json"
MAP_OUTPUT = ROOT / "data" / "qazgeo-regions-public.v1.geojson"
HEALTH_URL = "https://qgeo.tech/health/ready"
LAYERS_URL = "https://qgeo.tech/api/v1/layers"
REGIONAL_INDICATORS_URL = "https://qgeo.tech/api/v1/external-layers/regional-indicators"
REGIONS_GEOJSON_URL = "https://qgeo.tech/api/v1/mapregion/public/regions-geojson"


def fetch(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "qaz-industries-snapshot/1.0"})
    with urlopen(request, timeout=20) as response:  # nosec B310: fixed HTTPS URLs above
        return json.load(response)


def sanitize_regions(payload: dict) -> dict:
    if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise ValueError("QazGeo regions response is not a FeatureCollection")
    features = []
    for feature in payload["features"]:
        properties = feature.get("properties") or {}
        code = properties.get("code") or feature.get("id")
        geometry = feature.get("geometry")
        if not isinstance(code, str) or not isinstance(geometry, dict):
            raise ValueError("QazGeo region feature is missing safe identity or geometry")
        if geometry.get("type") not in {"Polygon", "MultiPolygon"} or not isinstance(geometry.get("coordinates"), list):
            raise ValueError("QazGeo region geometry must be Polygon or MultiPolygon")
        features.append({
            "type": "Feature",
            "id": code,
            "geometry": geometry,
            "properties": {
                "code": code,
                "name_ru": properties.get("region_name_ru") or properties.get("name_ru") or code,
                "name_en": properties.get("region_name_en") or properties.get("name_en") or code,
                "region_type": properties.get("region_type") or "region",
            },
        })
    if len(features) != 20:
        raise ValueError(f"expected 20 QazGeo regions, got {len(features)}")
    return {
        "type": "FeatureCollection",
        "qaz_schema_version": "qaz-industries-qazgeo-regions-public-v1",
        "source": REGIONS_GEOJSON_URL,
        "features": features,
    }


def snapshot() -> tuple[dict, dict]:
    health = fetch(HEALTH_URL)
    if health.get("status") != "ok" or health.get("service") != "qazgeo":
        raise ValueError("QazGeo health contract is not ready")
    coverage = {key: health.get(key) for key in ("regions", "cities", "pois")}
    if any(not isinstance(value, int) or value < 1 for value in coverage.values()):
        raise ValueError("QazGeo health response has invalid territorial coverage")

    layers = fetch(LAYERS_URL)
    region_layer = next((item for item in layers.get("layers", []) if item.get("id") == "regions"), None)
    if not isinstance(region_layer, dict) or region_layer.get("status") != "stable":
        raise ValueError("QazGeo stable regions layer is unavailable")

    regional = fetch(REGIONAL_INDICATORS_URL)
    regions_geojson = sanitize_regions(fetch(REGIONS_GEOJSON_URL))
    degraded = regional.get("degraded") is True
    if not degraded and not isinstance(regional.get("regions"), list):
        raise ValueError("QazGeo regional indicator contract is invalid")
    regional_module = {
        "id": "regional-indicators",
        "state": "degraded" if degraded else "ready",
        "reason": (
            "QazGeo подтвердил public contract, но его текущая QazLake-проекция региональных показателей имеет состояние "
            f"{regional.get('degraded_reason', 'upstream_unavailable')}; значения не публикуются."
            if degraded else "Публичная региональная проекция доступна для отдельного review перед публикацией."
        ),
    }
    result = {
        "schema_version": "qaz-industries-qazgeo-public-snapshot-v1",
        "status": "ready",
        "provider": {
            "service": health["service"],
            "source_revision": health["source_revision"],
            "health_url": HEALTH_URL,
            "layer_registry_url": LAYERS_URL,
            "geojson_url": REGIONS_GEOJSON_URL,
        },
        "retrieved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "publication_mode": "reviewed-static-snapshot",
        "coverage": coverage,
        "public_layers": [{
            "id": "regions",
            "label": region_layer["title"],
            "scope": "Национальная территориальная основа",
            "url": "https://qgeo.tech/api/v1/layers/regions",
        }],
        "map_contract": {
            "schema_version": regions_geojson["qaz_schema_version"],
            "asset": "data/qazgeo-regions-public.v1.geojson",
            "source_url": REGIONS_GEOJSON_URL,
            "feature_count": len(regions_geojson["features"]),
        },
        "limitations": [
            "Это территориальная основа и каталог публичных слоёв, а не отраслевой показатель.",
            "Браузер QAZ.INDUSTRIES не обращается к QazGeo напрямую; срез публикуется только после review как статический артефакт.",
            "QAZ.INDUSTRIES не отображает точные чувствительные координаты, raw QazLake observations или приватные source fields.",
        ],
        "unavailable_modules": [regional_module] if degraded else [],
    }
    return result, regions_geojson


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="replace the checked-in static snapshot after review")
    args = parser.parse_args()
    result, regions_geojson = snapshot()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
        MAP_OUTPUT.write_text(json.dumps(regions_geojson, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"updated {OUTPUT}")
        print(f"updated {MAP_OUTPUT}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
