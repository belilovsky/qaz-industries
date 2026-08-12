#!/usr/bin/env python3
"""Validate the AVDS4 route contract and the broader system-contract metric."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data" / "avds-coverage.v1.json"
SYSTEM_CONTRACT = ROOT / "data" / "avds-system-contract.v1.json"
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
PATTERNS = (
    "public-export-matrix",
    "evidence-source-registry",
    "geo-layer-registry",
    "related-question-grid",
    "analytics-panel",
    "chart-with-source",
    "period-comparison",
)
CATEGORY_IDS = (
    "routes",
    "tokens-themes",
    "components",
    "compositions",
    "states",
    "adaptive",
    "accessibility",
    "localization",
    "data-visualization",
    "version-discipline",
)
THEME_IDS = ("institutional", "editorial", "data-analytics", "map", "dark", "print")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def actual_route_gates() -> dict[str, bool]:
    pages = [(ROOT / name).read_text(encoding="utf-8") for name in PAGES]
    surface = "\n".join(
        pages
        + [
            (ROOT / "profile-view.js").read_text(encoding="utf-8"),
            (ROOT / "avds.css").read_text(encoding="utf-8"),
        ]
    )
    package = ROOT / "package.json"
    lockfile = ROOT / "package-lock.json"
    package_receipt_path = ROOT / "data" / "avds-package-runtime.v1.json"
    package_uses_ui_kit = False
    if package.is_file() and lockfile.is_file() and package_receipt_path.is_file():
        try:
            package_json = json.loads(package.read_text(encoding="utf-8"))
            lock = json.loads(lockfile.read_text(encoding="utf-8"))
            package_receipt = json.loads(package_receipt_path.read_text(encoding="utf-8"))
            package_runtime = package_receipt.get("package", {})
            artifact_contract = package_receipt.get("artifact", {})
            runtime_contract = package_receipt.get("runtime", {})
            tarball = ROOT / package_runtime.get("dependency", "")
            artifact = ROOT / artifact_contract.get("path", "")
            locked_package = lock.get("packages", {}).get("node_modules/@sgeo/ui-kit", {})
            package_uses_ui_kit = (
                package_json.get("dependencies", {}).get("@sgeo/ui-kit") == "file:vendor/sgeo-ui-kit-4.6.0.tgz"
                and locked_package.get("version") == "4.6.0"
                and locked_package.get("resolved") == "file:vendor/sgeo-ui-kit-4.6.0.tgz"
                and package_receipt.get("schema_version") == "qaz-industries-avds-package-runtime-v1"
                and package_runtime.get("name") == "@sgeo/ui-kit"
                and package_runtime.get("version") == "4.6.0"
                and runtime_contract.get("kind") == "css-token-export"
                and runtime_contract.get("javascript_added") is False
                and runtime_contract.get("pages") == list(PAGES)
                and tarball.is_file()
                and artifact.is_file()
                and sha256(tarball) == package_runtime.get("tarball_sha256")
                and sha256(artifact) == artifact_contract.get("sha256")
                and all('href="avds-package-runtime.css"' in page for page in pages)
            )
        except (OSError, TypeError, json.JSONDecodeError):
            package_uses_ui_kit = False
    registration = ROOT / "avds-consumer.json"
    consumer_is_registered = False
    if registration.is_file():
        try:
            contract = json.loads(registration.read_text(encoding="utf-8"))
            catalog = contract.get("catalog_registration", {})
            adoption = contract.get("adoption", {})
            consumer_is_registered = (
                contract.get("schema_version") == "qaz-industries-avds-consumer-v1"
                and contract.get("product_id") == "qaz-industries"
                and contract.get("canonical_url") == "https://qaz.industries/"
                and contract.get("integration_mode") == "static-contract"
                and contract.get("avds_version") == "4.6.0"
                and adoption.get("package_runtime") is True
                and adoption.get("package_runtime_receipt") == "data/avds-package-runtime.v1.json"
                and catalog.get("consumer_id") == "qaz_industries"
                and catalog.get("state") == "source-registered"
            )
        except (OSError, TypeError, json.JSONDecodeError):
            consumer_is_registered = False
    shell_contract = (
        'data-avds-pattern="app-shell"',
        'data-avds-pattern="site-footer"',
        "av-app-shell__brand",
        "av-app-shell__nav",
        "av-app-shell__actions",
        "av-app-shell__mobile-nav",
        "av-site-footer__brand",
        "av-site-footer__summary",
        "av-site-footer__meta",
    )
    shell_is_canonical = all(all(marker in page for marker in shell_contract) for page in pages)
    return {
        "root-marker": all('data-design-system="avds4"' in page for page in pages),
        "token-layer": all('href="avds-tokens.css"' in page for page in pages),
        "component-layer": all('href="avds.css"' in page for page in pages),
        "theme-contract": all('data-av-theme="institutional"' in page and "data-theme-toggle" in page for page in pages),
        "buttons": "av-button" in surface,
        "cards": "av-card" in surface,
        "statuses": all(component in surface for component in ("av-badge", "av-chip", "av-alert")),
        "tables": "av-table" in surface,
        "public-patterns": all(f'data-avds-pattern="{pattern}"' in surface for pattern in PATTERNS),
        "package-runtime": package_uses_ui_kit,
        "consumer-registration": consumer_is_registered,
        "shell-parity": shell_is_canonical,
    }


def validate_system_contract(contract: dict[str, object], route_gates: dict[str, bool]) -> list[dict[str, object]]:
    if contract.get("schema_version") != "qaz-industries-avds-system-contract-v1":
        raise ValueError("AVDS system-contract schema")
    if contract.get("product_id") != "qaz-industries":
        raise ValueError("AVDS system-contract product")
    provenance = contract.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("AVDS system-contract provenance")
    if not re.fullmatch(r"4\.\d+\.\d+", str(provenance.get("avds_version", ""))):
        raise ValueError("AVDS system-contract version")
    for field in ("package_source_revision", "control_plane_revision"):
        if not re.fullmatch(r"[0-9a-f]{40}", str(provenance.get(field, ""))):
            raise ValueError(f"AVDS system-contract {field}")
    if not isinstance(provenance.get("synchronized_at"), str) or not provenance["synchronized_at"].endswith("Z"):
        raise ValueError("AVDS system-contract synchronization date")
    if provenance.get("package_runtime_receipt") != "data/avds-package-runtime.v1.json":
        raise ValueError("AVDS system-contract package receipt")
    connected = provenance.get("connected_files")
    if not isinstance(connected, list) or len(connected) < 5:
        raise ValueError("AVDS system-contract connected file inventory")
    for item in connected:
        if not isinstance(item, dict):
            raise ValueError("AVDS system-contract file entry")
        relative_path = item.get("path")
        if not isinstance(relative_path, str) or relative_path.startswith("/") or ".." in Path(relative_path).parts:
            raise ValueError("AVDS system-contract unsafe file path")
        target = ROOT / relative_path
        if not target.is_file() or item.get("sha256") != sha256(target):
            raise ValueError(f"AVDS system-contract stale digest: {relative_path}")
    deviations = contract.get("local_deviations")
    if not isinstance(deviations, list) or not deviations:
        raise ValueError("AVDS system-contract local deviations")
    for item in deviations:
        if not isinstance(item, dict) or not item.get("id") or item.get("status") not in {"accepted", "open"} or not item.get("detail"):
            raise ValueError("AVDS system-contract invalid local deviation")
    themes = contract.get("themes")
    if not isinstance(themes, list) or tuple(item.get("id") for item in themes if isinstance(item, dict)) != THEME_IDS:
        raise ValueError("AVDS system-contract theme matrix")
    tokens_source = (ROOT / "avds-tokens.css").read_text(encoding="utf-8")
    theme_source = (ROOT / "theme.js").read_text(encoding="utf-8")
    if any(item.get("status") != "verified" or not item.get("selector") for item in themes):
        raise ValueError("AVDS system-contract theme matrix must be implemented or explicitly removed")
    if any(item["selector"] not in tokens_source for item in themes):
        raise ValueError("AVDS system-contract theme selector is not in token layer")
    if any(f"'{theme_id}'" not in theme_source for theme_id in THEME_IDS if theme_id != "institutional"):
        raise ValueError("AVDS system-contract theme is not in runtime theme cycle")
    categories = contract.get("categories")
    if not isinstance(categories, list) or tuple(item.get("id") for item in categories if isinstance(item, dict)) != CATEGORY_IDS:
        raise ValueError("AVDS system-contract category set")
    result: list[dict[str, object]] = []
    for category in categories:
        if not isinstance(category, dict):
            raise ValueError("AVDS system-contract category")
        requirements = category.get("requirements")
        verified = category.get("verified")
        evidence = category.get("evidence")
        if not isinstance(requirements, list) or not requirements or len(requirements) != len(set(requirements)):
            raise ValueError(f"AVDS system-contract {category.get('id')}: requirements")
        if not isinstance(verified, list) or not set(verified).issubset(requirements):
            raise ValueError(f"AVDS system-contract {category.get('id')}: verified set")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError(f"AVDS system-contract {category.get('id')}: evidence")
        for path in evidence:
            if not isinstance(path, str) or not (ROOT / path).is_file():
                raise ValueError(f"AVDS system-contract {category.get('id')}: missing evidence {path}")
        if category["id"] == "routes":
            if set(requirements) != set(route_gates) or set(verified) != {gate_id for gate_id, passed in route_gates.items() if passed}:
                raise ValueError("AVDS system-contract route gate drift")
        passed = len(verified)
        total = len(requirements)
        result.append({
            "id": category["id"],
            "label": category.get("label"),
            "passed": passed,
            "total": total,
            "coverage_percent": round(passed * 100 / total),
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh the derived public coverage receipt")
    args = parser.parse_args()
    try:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        contract = json.loads(SYSTEM_CONTRACT.read_text(encoding="utf-8"))
        route_gates = actual_route_gates()
        dimensions = validate_system_contract(contract, route_gates)
        declared_gates = {item["id"]: item for item in receipt.get("gates", [])}
        if set(declared_gates) != set(route_gates):
            raise ValueError("AVDS route gate set differs from the coverage receipt")
        passed = sum(item["passed"] for item in dimensions)
        total = sum(item["total"] for item in dimensions)
        percent = round(passed * 100 / total)
        version = contract["provenance"]["avds_version"]
        badge = f"AVDS {version}-{percent}"
        route_passed = sum(route_gates.values())
        route_total = len(route_gates)
        if args.write:
            for gate_id, status in route_gates.items():
                declared_gates[gate_id]["passed"] = status
            receipt["evaluated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            receipt["avds"].update({
                "version": version,
                "source_revision": contract["provenance"]["package_source_revision"],
                "control_plane_revision": contract["provenance"]["control_plane_revision"],
            })
            receipt["method"] = {
                "kind": "avds-system-contract-categories",
                "passed": passed,
                "total": total,
                "note": "Общий показатель считает только verified requirements десяти категорий AVDS system contract; route contract публикуется отдельно.",
            }
            receipt["route_contract"] = {
                "passed": route_passed,
                "total": route_total,
                "coverage_percent": round(route_passed * 100 / route_total),
                "note": "Базовое покрытие маршрутов и consumer integration; не является общей зрелостью дизайн-системы.",
            }
            receipt["system_contract"] = "data/avds-system-contract.v1.json"
            receipt["dimensions"] = dimensions
            receipt["coverage_percent"] = percent
            receipt["badge"] = badge
            RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            mismatches = [gate_id for gate_id, status in route_gates.items() if declared_gates[gate_id]["passed"] is not status]
            if mismatches:
                raise ValueError(f"stale AVDS route gate states: {', '.join(mismatches)}; run with --write")
            if receipt.get("avds", {}).get("version") != version:
                raise ValueError("stale AVDS version; run with --write")
            if receipt.get("method", {}).get("passed") != passed or receipt["method"].get("total") != total:
                raise ValueError("stale AVDS system coverage counts; run with --write")
            if receipt.get("route_contract", {}).get("passed") != route_passed or receipt["route_contract"].get("total") != route_total:
                raise ValueError("stale AVDS route coverage counts; run with --write")
            if receipt.get("dimensions") != dimensions:
                raise ValueError("stale AVDS dimensions; run with --write")
            if receipt.get("coverage_percent") != percent or receipt.get("badge") != badge:
                raise ValueError("stale AVDS badge; run with --write")
        print(f"AVDS system coverage: {percent}% ({passed}/{total}), route contract: {route_passed}/{route_total}, badge={badge}")
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"AVDS SYSTEM CONTRACT FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
