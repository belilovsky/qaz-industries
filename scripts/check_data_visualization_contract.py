#!/usr/bin/env python3
"""Validate data-visualization grammar and source/table alternatives."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "avds-data-visualization-contract.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        require(contract.get("schema_version") == "qaz-industries-avds-data-visualization-contract-v1", "visualization schema")
        palette = contract.get("palette") or {}
        require(set(palette) >= {"ready", "partial", "gap", "map_region", "map_selected", "map_focus"}, "visualization palette")
        visualizations = contract.get("visualizations")
        require(isinstance(visualizations, list) and len(visualizations) == 4, "visualization set")
        required_fields = {"id", "kind", "selector", "source", "legend", "scale", "axes", "units", "precision", "missing_values", "table_alternative", "data_status"}
        for item in visualizations:
            require(required_fields <= set(item), f"visualization fields: {item.get('id')}")
            require(item.get("source") and item.get("units") and item.get("precision") and item.get("missing_values"), f"visualization provenance: {item.get('id')}")
            require(isinstance(item.get("data_status"), list) and item["data_status"], f"visualization states: {item.get('id')}")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        profile = (ROOT / "industry.html").read_text(encoding="utf-8")
        profile_view = (ROOT / "profile-view.js").read_text(encoding="utf-8")
        require('data-avds-viz="qazgeo-map"' in index and 'qazgeo-map__legend' in index, "map legend contract")
        require('data-avds-viz="ordinal-coverage"' in profile and 'id="compare-table"' in profile, "coverage chart/table contract")
        require('data-avds-viz="period-comparison"' in profile and 'id="period-comparison"' in profile, "period comparison contract")
        for marker in ("av-coverage-chart__legend", "av-coverage-chart__track", "av-coverage-chart__source", "localeContract().unit"):
            require(marker in profile_view or marker in profile, f"visualization implementation marker missing: {marker}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"DATA VISUALIZATION CONTRACT FAILED: {error}", file=sys.stderr)
        return 1
    print("data visualization contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
