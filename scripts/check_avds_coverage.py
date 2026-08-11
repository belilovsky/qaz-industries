#!/usr/bin/env python3
"""Recompute and validate the public AVDS consumer-coverage receipt."""

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
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
PATTERNS = (
    "public-export-matrix",
    "evidence-source-registry",
    "geo-layer-registry",
    "related-question-grid",
)


def actual_gates() -> dict[str, bool]:
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
                and hashlib.sha256(tarball.read_bytes()).hexdigest() == package_runtime.get("tarball_sha256")
                and hashlib.sha256(artifact.read_bytes()).hexdigest() == artifact_contract.get("sha256")
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh gate states and percentage")
    parser.add_argument("--avds-version", help="Update the verified AVDS release version")
    parser.add_argument("--source-revision", help="Update the verified AVDS source revision")
    args = parser.parse_args()

    try:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        gates = actual_gates()
        declared = {item["id"]: item for item in receipt["gates"]}
        if set(declared) != set(gates):
            raise ValueError("AVDS gate set differs from the coverage contract")

        version = args.avds_version or receipt["avds"]["version"]
        if not re.fullmatch(r"4\.\d+\.\d+", version):
            raise ValueError("AVDS version must use 4.x.x format")
        if args.source_revision and not re.fullmatch(r"[0-9a-f]{40}", args.source_revision):
            raise ValueError("AVDS source revision must be a full lowercase Git SHA")

        passed = sum(gates.values())
        total = len(gates)
        percent = round(passed * 100 / total)
        badge = f"AVDS {version}-{percent}"

        if args.write:
            for gate_id, status in gates.items():
                declared[gate_id]["passed"] = status
            receipt["evaluated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            receipt["avds"]["version"] = version
            if args.source_revision:
                receipt["avds"]["source_revision"] = args.source_revision
            receipt["method"].update({"passed": passed, "total": total})
            receipt["coverage_percent"] = percent
            receipt["badge"] = badge
            RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            mismatches = [gate_id for gate_id, status in gates.items() if declared[gate_id]["passed"] is not status]
            if mismatches:
                raise ValueError(f"stale AVDS gate states: {', '.join(mismatches)}; run with --write")
            if receipt["method"]["passed"] != passed or receipt["method"]["total"] != total:
                raise ValueError("stale AVDS coverage counts; run with --write")
            if receipt["coverage_percent"] != percent or receipt["badge"] != badge:
                raise ValueError("stale AVDS badge; run with --write")

        print(f"AVDS coverage: {percent}% ({passed}/{total}), badge={badge}")
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"AVDS COVERAGE FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
