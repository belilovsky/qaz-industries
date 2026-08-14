#!/usr/bin/env python3
"""Fail closed when QAZ.INDUSTRIES editorial work is represented as completed without evidence."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REQUIRED_CHECKS = {"sourceReview", "rightsReview", "legalReview"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def https(value: object, label: str) -> None:
    require(isinstance(value, str) and urlparse(value).scheme == "https", f"{label}: HTTPS required")


def main() -> int:
    try:
        ledger = json.loads((DATA / "edpol-editorial-ledger.v1.json").read_text(encoding="utf-8"))
        registry = json.loads((DATA / "reviewed-source-registry.v1.json").read_text(encoding="utf-8"))
        require(ledger.get("schema_version") == "qaz-industries-edpol-editorial-ledger-v1", "ledger schema")
        require(ledger.get("product_id") == "qaz-industries", "ledger product")
        require(ledger.get("status") == "review-required", "ledger must remain review-required until recorded evidence exists")
        integration = ledger.get("integration") or {}
        for field in ("control_plane", "risk_register", "source_check", "article_trust_schema"):
            https(integration.get(field), f"integration {field}")
        require(integration.get("mode") == "local-static-fail-closed", "integration mode")
        require(integration.get("stores_content_bodies") is False, "content bodies must stay local")
        require(integration.get("writes_edpol_production") is False, "production writes require explicit approval")
        require(integration.get("automatic_publication") is False, "automatic publication is forbidden")

        registry_by_id = {item.get("id"): item for item in registry.get("sources", [])}
        reviews = ledger.get("source_reviews")
        require(isinstance(reviews, list) and {item.get("source_id") for item in reviews} == set(registry_by_id), "source review set")
        for review in reviews:
            source = registry_by_id[review["source_id"]]
            require(review.get("canonical_url") == source.get("url"), f"{review['source_id']}: canonical URL differs from registry")
            require(review.get("status") == "review-required", f"{review['source_id']}: unrecorded review may not be marked complete")
            required = set(review.get("required_checks") or [])
            require(required and required <= REQUIRED_CHECKS and "sourceReview" in required and "rightsReview" in required, f"{review['source_id']}: required checks")
            require(review.get("reviewer_id") is None and review.get("reviewed_at") is None and review.get("capture_manifest") is None, f"{review['source_id']}: evidence fields require a recorded review decision")

        materials = ledger.get("materials")
        require(isinstance(materials, list) and len(materials) == 6, "material scope")
        material_ids = [item.get("id") for item in materials]
        require(len(set(material_ids)) == len(material_ids) and all(isinstance(item, str) and item for item in material_ids), "material IDs")
        for material in materials:
            require(isinstance(material.get("paths"), list) and material["paths"], f"{material['id']}: paths")
            source_ids = set(material.get("source_ids") or [])
            require(source_ids and source_ids <= set(registry_by_id), f"{material['id']}: source IDs")
            required = set(material.get("required_checks") or [])
            require(required and required <= REQUIRED_CHECKS and "sourceReview" in required and "rightsReview" in required, f"{material['id']}: required checks")
            require(material.get("decision") == "needs-review", f"{material['id']}: must remain in review")
            require(material.get("reviewer_id") is None and material.get("evaluated_at") is None, f"{material['id']}: reviewer evidence is incomplete")
            require(material.get("ai_disclosure") == "not-declared", f"{material['id']}: AI state must not be inferred")
            require(material.get("language_parity") == "not-assessed", f"{material['id']}: language parity must not be inferred")
        macro = next(item for item in materials if item["id"] == "macro-context")
        require(set(macro.get("risk_rule_ids") or []) == {"public-impact.health-finance", "rights.third-party-material"}, "macro risk rules")
        corrections = ledger.get("corrections") or {}
        require(corrections == {"status": "not-established", "public_log": None, "issue_intake": None}, "corrections status must stay explicit")
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"EdPol editorial ledger: FAILED: {error}")
        return 1
    print("EdPol editorial ledger: OK (6 materials and 6 sources remain fail-closed pending human review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
