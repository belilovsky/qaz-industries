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
HEALTH_URL = "https://qgeo.tech/health/ready"
LAYERS_URL = "https://qgeo.tech/api/v1/layers"
REGIONAL_INDICATORS_URL = "https://qgeo.tech/api/v1/external-layers/regional-indicators"


def fetch(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "qaz-industries-snapshot/1.0"})
    with urlopen(request, timeout=20) as response:  # nosec B310: fixed HTTPS URLs above
        return json.load(response)


def snapshot() -> dict:
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
    return {
        "schema_version": "qaz-industries-qazgeo-public-snapshot-v1",
        "status": "ready",
        "provider": {
            "service": health["service"],
            "source_revision": health["source_revision"],
            "health_url": HEALTH_URL,
            "layer_registry_url": LAYERS_URL,
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
        "limitations": [
            "Это территориальная основа и каталог публичных слоёв, а не отраслевой показатель.",
            "Браузер QAZ.INDUSTRIES не обращается к QazGeo напрямую; срез публикуется только после review как статический артефакт.",
            "QAZ.INDUSTRIES не отображает точные чувствительные координаты, raw QazLake observations или приватные source fields.",
        ],
        "unavailable_modules": [regional_module] if degraded else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="replace the checked-in static snapshot after review")
    args = parser.parse_args()
    result = snapshot()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"updated {OUTPUT}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
