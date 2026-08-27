#!/usr/bin/env python3
"""Refresh derived AVDS system-contract provenance after a canonical UI change."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "avds-system-contract.v1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write refreshed connected-file digests")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    provenance = contract.get("provenance") or {}
    connected = provenance.get("connected_files") or []
    if contract.get("schema_version") != "qaz-industries-avds-system-contract-v1" or not connected:
        raise SystemExit("AVDS system contract: unsupported provenance")
    refreshed = []
    for item in connected:
        relative = item.get("path") if isinstance(item, dict) else None
        target = ROOT / relative if isinstance(relative, str) else None
        if target is None or not target.is_file():
            raise SystemExit(f"AVDS system contract: missing connected file {relative}")
        refreshed.append({"path": relative, "sha256": digest(target)})
    if not args.write:
        if refreshed != connected:
            raise SystemExit("AVDS system contract: stale connected-file digests; run with --write")
        print("AVDS system contract provenance: OK")
        return 0
    provenance["connected_files"] = refreshed
    provenance["synchronized_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    contract["provenance"] = provenance
    CONTRACT.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"AVDS system contract provenance: refreshed {len(refreshed)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
