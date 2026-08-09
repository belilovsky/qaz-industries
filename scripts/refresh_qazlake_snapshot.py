#!/usr/bin/env python3
"""Fetch the narrow public QazLake macro snapshot for reviewed static release use."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "qazlake-public-snapshot.v1.json"
HEALTH_URL = "https://qlake.tech/health"
INDICATORS_URL = "https://qlake.tech/api/economy/indicators"
ALLOWED = ("NBK_BASE_RATE", "CPI_YOY", "CPI_MOM")
SOURCE_URLS = {
    "NBK_BASE_RATE": "https://nationalbank.kz/",
    "CPI_YOY": "https://stat.gov.kz/",
    "CPI_MOM": "https://stat.gov.kz/",
}


def fetch(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "qaz-industries-snapshot/1.0"})
    with urlopen(request, timeout=20) as response:  # nosec B310: fixed HTTPS URLs above
        return json.load(response)


def snapshot() -> dict:
    health = fetch(HEALTH_URL)
    if health.get("status") != "ok" or health.get("service") != "qazlake-lite-api":
        raise ValueError("QazLake health contract is not ready")
    payload = fetch(INDICATORS_URL)
    if payload.get("includes_forecasts") is not False:
        raise ValueError("QazLake snapshot unexpectedly includes forecasts")
    by_id = {item.get("indicator_code"): item for item in payload.get("indicators", [])}
    if set(ALLOWED) - set(by_id):
        raise ValueError("QazLake snapshot is missing required macro indicators")
    indicators = []
    for indicator_id in ALLOWED:
        item = by_id[indicator_id]
        if item.get("is_forecast") is not False or not isinstance(item.get("value"), (int, float)):
            raise ValueError(f"invalid public macro indicator: {indicator_id}")
        indicators.append({
            "id": indicator_id,
            "label": item["indicator_name"],
            "value": item["value"],
            "unit": item["unit"],
            "as_of": item["indicator_date"],
            "source": item["source"],
            "source_url": SOURCE_URLS[indicator_id],
            "is_forecast": False,
        })
    return {
        "schema_version": "qaz-industries-qazlake-public-snapshot-v1",
        "status": "ready",
        "provider": {
            "service": health["service"],
            "source_revision": health["source_revision"],
            "health_url": HEALTH_URL,
            "endpoint": INDICATORS_URL,
        },
        "retrieved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "publication_mode": "reviewed-static-snapshot",
        "limitations": [
            "Срез является общеэкономическим контекстом и не заменяет отраслевые показатели.",
            "Браузер QAZ.INDUSTRIES не обращается к QazLake напрямую; файл собирается и проверяется как статический артефакт.",
            "Региональные и географические QazLake endpoints не опубликованы в текущей public API revision и показаны как degraded, а не как пустые данные."
        ],
        "indicators": indicators,
        "unavailable_modules": [
            {"id": "regional-indicators", "state": "degraded", "reason": "Публичный endpoint региональных показателей недоступен в текущей ревизии QazLake API."},
            {"id": "water-catalogue", "state": "degraded", "reason": "Публичные endpoints водоёмов и гидропостов недоступны в текущей ревизии QazLake API."}
        ],
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
