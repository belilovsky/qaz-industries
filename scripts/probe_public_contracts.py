#!/usr/bin/env python3
"""Run every public upstream probe and apply the reviewed degradation policy."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
QAZLAKE_SNAPSHOT = ROOT / "data" / "qazlake-public-snapshot.v1.json"
MAX_SNAPSHOT_AGE_DAYS = 31

PROBES = (
    ("qazlake", ("python3", "scripts/refresh_qazlake_snapshot.py")),
    ("qazgeo", ("python3", "scripts/refresh_qazgeo_snapshot.py")),
    ("qazgeo-layer-registry", ("python3", "scripts/refresh_qazgeo_layer_registry.py")),
    ("sector-sources", ("python3", "scripts/check_sector_sources.py")),
)


def validate_qazlake_snapshot(
    path: Path = QAZLAKE_SNAPSHOT,
    *,
    now: datetime | None = None,
) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "qaz-industries-qazlake-public-snapshot-v1":
        raise ValueError("QazLake snapshot schema is invalid")
    if payload.get("status") != "ready":
        raise ValueError("QazLake snapshot is not a reviewed ready snapshot")
    indicators = payload.get("indicators")
    if not isinstance(indicators, list) or len(indicators) != 3:
        raise ValueError("QazLake snapshot must contain three reviewed indicators")
    if any(item.get("is_forecast") is not False for item in indicators):
        raise ValueError("QazLake snapshot contains a forecast")
    observed = datetime.fromisoformat(payload["retrieved_at"].replace("Z", "+00:00"))
    current = now or datetime.now(timezone.utc)
    age_days = (current - observed).days
    if age_days < 0 or age_days > MAX_SNAPSHOT_AGE_DAYS:
        raise ValueError(f"QazLake snapshot is stale ({age_days} days)")
    return age_days


def run_probe(
    name: str,
    command: tuple[str, ...],
    output_dir: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict:
    completed = runner(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output_path = output_dir / f"{name}.json"
    if completed.returncode == 0:
        output_path.write_text(completed.stdout, encoding="utf-8")
        return {"id": name, "state": "ready", "blocking": False, "exit_code": 0}

    error = completed.stderr.strip()[-1000:] or f"probe exited {completed.returncode}"
    if name == "qazlake":
        try:
            age_days = validate_qazlake_snapshot()
        except (KeyError, OSError, ValueError, json.JSONDecodeError) as snapshot_error:
            result = {
                "id": name,
                "state": "blocked",
                "blocking": True,
                "exit_code": completed.returncode,
                "reason": str(snapshot_error),
            }
        else:
            result = {
                "id": name,
                "state": "degraded",
                "blocking": False,
                "exit_code": completed.returncode,
                "snapshot_age_days": age_days,
                "reason": "Upstream contract is unavailable; retained the last reviewed static snapshot.",
            }
    else:
        result = {
            "id": name,
            "state": "blocked",
            "blocking": True,
            "exit_code": completed.returncode,
            "reason": error,
        }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results = [
        run_probe(name, command, args.output_dir) for name, command in PROBES
    ]
    summary = {
        "schema_version": "qaz-industries-public-contract-probe-summary-v1",
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "policy": {
            "qazlake_unavailable": "retain-reviewed-snapshot-and-report-degraded",
            "qazlake_max_snapshot_age_days": MAX_SNAPSHOT_AGE_DAYS,
            "other_probe_failure": "block",
        },
        "results": results,
        "blocking_failures": sum(item["blocking"] for item in results),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["blocking_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
