#!/usr/bin/env python3
"""Enforce the reviewed Russian user-surface terminology contract."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "content" / "terminology.ru.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        require(contract.get("schema_version") == "qaz-industries-terminology-v1", "unexpected terminology schema")
        require(contract.get("locale") == "ru", "terminology locale must be ru")
        required_terms = {"snapshot", "reviewed", "layer registry", "contract_only", "release", "raw data"}
        require(required_terms <= set(contract.get("preferred_terms", {})), "preferred terminology is incomplete")
        forbidden = [phrase.casefold() for phrase in contract.get("forbidden_user_phrases", [])]
        require(forbidden and all(forbidden), "forbidden phrase list is empty or invalid")
        for filename in contract.get("user_surface_files", []):
            path = ROOT / filename
            require(path.is_file(), f"missing user surface: {filename}")
            source = path.read_text(encoding="utf-8").casefold()
            for phrase in forbidden:
                require(phrase not in source, f"{filename}: forbidden user phrase remains: {phrase}")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"CONTENT CHECK FAILED: {error}", file=sys.stderr)
        return 1
    print("content terminology: OK (ru)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
