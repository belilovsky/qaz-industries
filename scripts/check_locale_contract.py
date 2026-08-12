#!/usr/bin/env python3
"""Validate locale, number/date/unit and state-copy contracts."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from build_locale_catalog import inventory_hash, source_inventory


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "content" / "locale-contract.v1.json"
CATALOG = ROOT / "data" / "ui-locale.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        require(contract.get("schema_version") == "qaz-industries-locale-contract-v1", "locale schema")
        require(contract.get("default_locale") == "ru-RU" and contract.get("interface_language") == "ru", "default locale")
        require(contract.get("formatting_locales") == ["ru-RU", "kk-KZ", "en-US"], "formatting locale matrix")
        rules = contract.get("rules") or {}
        require(set(rules) == {"number", "date", "unit", "line_breaks", "messages"} and all(rules.values()), "locale rules")
        messages = contract.get("messages") or {}
        required_messages = {"loading", "empty", "error", "offline", "stale", "success", "contract-only"}
        require(required_messages <= set(messages) and all(isinstance(messages[key], str) and messages[key] for key in required_messages), "state messages")
        source = (ROOT / "locale.js").read_text(encoding="utf-8")
        profile = (ROOT / "profile-view.js").read_text(encoding="utf-8")
        for symbol in ("SUPPORTED_LOCALES", "number", "date", "unit", "snapshotState", "message"):
            require(symbol in source, f"locale runtime symbol missing: {symbol}")
        require("localeContract().unit" in profile and "localeContract().snapshotState" in profile, "profile must consume locale contract")
        for message in messages.values():
            require(message in source or message in profile, f"locale message not wired: {message}")
        terminology = json.loads((ROOT / "content" / "terminology.ru.json").read_text(encoding="utf-8"))
        require(terminology.get("locale") == "ru" and terminology.get("preferred_terms"), "Russian terminology contract")
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        require(catalog.get("schema_version") == "qaz-industries-ui-locale-v1", "UI locale catalog schema")
        require(catalog.get("supported_locales") == ["ru-RU", "kk-KZ", "en-US"], "UI locale catalog matrix")
        inventory = source_inventory()
        receipt = catalog.get("inventory") or {}
        require(receipt.get("source_count") == len(inventory), "UI locale catalog source count")
        require(receipt.get("source_sha256") == inventory_hash(inventory), "UI locale catalog inventory hash")
        for locale in ("ru-RU", "kk-KZ", "en-US"):
            mapping = catalog.get("translations", {}).get(locale, {})
            require(set(mapping) == set(inventory) and all(isinstance(value, str) and value.strip() for value in mapping.values()), f"UI locale catalog coverage: {locale}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"LOCALE CONTRACT FAILED: {error}", file=sys.stderr)
        return 1
    print("locale contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
