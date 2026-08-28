#!/usr/bin/env python3
"""Build and verify public machine-discovery files from one safe allowlist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "public-discovery.v1.json"
SCHEMA = "qaz-industries-public-discovery-v1"
AI_SCHEMA = "qaz-industries-ai-index-v1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_source() -> dict:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    require(payload.get("schema_version") == SCHEMA, "discovery schema")
    require(payload.get("product_id") == "qaz-industries", "discovery product")
    canonical = payload.get("canonical_url")
    parsed = urlparse(canonical if isinstance(canonical, str) else "")
    require(parsed.scheme == "https" and parsed.netloc == "qaz.industries" and not parsed.path, "discovery canonical URL")
    require(payload.get("language") == "ru", "discovery language")
    require(payload.get("locales") == ["ru", "kk", "en"], "discovery locales")
    policy = payload.get("policy")
    require(isinstance(policy, dict), "discovery policy")
    require(policy.get("generated_outputs") == ["ai-index.json", "llms.txt"], "discovery outputs")
    require(policy.get("public_allowlist_only") is True, "discovery public allowlist")
    require(policy.get("direct_browser_upstream_access") is False, "discovery browser upstream boundary")
    require(policy.get("external_runtime_data_calls") is False, "discovery runtime boundary")
    require(policy.get("credentials_and_private_data") == "excluded", "discovery privacy boundary")
    entries = payload.get("entrypoints")
    require(isinstance(entries, list) and entries, "discovery entrypoints")
    ids: set[str] = set()
    paths: set[str] = set()
    for entry in entries:
        require(isinstance(entry, dict), "discovery entrypoint object")
        identifier = entry.get("id")
        path = entry.get("path")
        require(isinstance(identifier, str) and identifier and identifier.replace("-", "").isalnum(), "discovery entrypoint id")
        require(identifier not in ids, f"duplicate discovery entrypoint id: {identifier}")
        require(isinstance(path, str) and path.startswith("/") and not path.startswith("//"), f"discovery path: {identifier}")
        require("?" not in path and "#" not in path, f"discovery path query or fragment: {identifier}")
        require(path not in paths, f"duplicate discovery path: {path}")
        require(entry.get("kind") in {"html", "json"}, f"discovery entrypoint kind: {identifier}")
        require(isinstance(entry.get("title_ru"), str) and entry["title_ru"].strip(), f"discovery title: {identifier}")
        ids.add(identifier)
        paths.add(path)
    return payload


def render(payload: dict) -> tuple[str, str]:
    canonical = payload["canonical_url"]
    entrypoints = [
        {
            "id": entry["id"],
            "kind": entry["kind"],
            "url": urljoin(canonical + "/", entry["path"].lstrip("/")),
            "title_ru": entry["title_ru"],
        }
        for entry in payload["entrypoints"]
    ]
    ai_index = {
        "schema_version": AI_SCHEMA,
        "product_id": payload["product_id"],
        "canonical_url": canonical,
        "language": payload["language"],
        "locales": payload["locales"],
        "generated_from": "data/public-discovery.v1.json",
        "public_safe": True,
        "boundaries": {
            "direct_browser_upstream_access": False,
            "external_runtime_data_calls": False,
            "credentials_and_private_data": "excluded",
        },
        "entrypoints": entrypoints,
    }
    lines = [
        "# QAZ.INDUSTRIES",
        "",
        "> Публичный статический навигатор по проверенным интерфейсам индустриального продукта Казахстана.",
        "",
        "Generated from: data/public-discovery.v1.json",
        "",
        "## Public interfaces",
        "",
    ]
    lines.extend(f"- {entry['title_ru']}: {entry['url']}" for entry in entrypoints)
    lines.extend([
        "",
        "## Boundary",
        "",
        "- Используйте только перечисленные публичные URL.",
        "- Это статический продукт: браузер не выполняет прямых upstream-вызовов к QazLake или QazGeo.",
        "- В этом индексе отсутствуют учетные данные, приватные данные и непроверенные внешние snapshots.",
        "",
    ])
    return json.dumps(ai_index, ensure_ascii=False, indent=2) + "\n", "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.check and args.output_dir != ROOT:
        raise SystemExit("--check only verifies the canonical root")
    try:
        payload = load_source()
        ai_index, llms = render(payload)
        expected = {"ai-index.json": ai_index, "llms.txt": llms}
        if args.check:
            for name, content in expected.items():
                path = ROOT / name
                require(path.is_file(), f"missing generated discovery file: {name}")
                require(path.read_text(encoding="utf-8") == content, f"stale generated discovery file: {name}")
            print("public discovery: OK")
            return 0
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in expected.items():
            (args.output_dir / name).write_text(content, encoding="utf-8")
        print(args.output_dir)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"public discovery: {error}") from error


if __name__ == "__main__":
    raise SystemExit(main())
