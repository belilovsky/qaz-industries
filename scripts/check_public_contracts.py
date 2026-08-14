#!/usr/bin/env python3
"""Validate public QAZ.INDUSTRIES data contracts without external services."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def https(value: object, label: str) -> None:
    require(isinstance(value, str) and urlparse(value).scheme == "https", f"{label}: HTTPS required")


def main() -> int:
    try:
        profiles = load("industry-profiles.v1.json")
        require(profiles["schema_version"] == "qaz-industries-public-profiles-v1", "profiles schema")
        require(len(profiles["profiles"]) == 4, "expected four industry profiles")
        for profile in profiles["profiles"]:
            require(isinstance(profile.get("id"), str), "profile id")
            require(isinstance(profile.get("source_release_id"), str) and profile["source_release_id"], f"profile {profile.get('id')}: source release")
            https(profile.get("source"), f"profile {profile.get('id')}")
        for entrypoint in profiles["machine_entrypoints"]:
            https(entrypoint.get("url"), "machine entrypoint")

        snapshot = load("qazlake-public-snapshot.v1.json")
        require(snapshot["schema_version"] == "qaz-industries-qazlake-public-snapshot-v1", "snapshot schema")
        require(snapshot["status"] == "ready", "snapshot must state ready")
        retrieved_at = datetime.fromisoformat(snapshot["retrieved_at"].replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - retrieved_at).days
        require(0 <= age_days <= 31, f"snapshot is stale ({age_days} days); refresh before release")
        https(snapshot["provider"]["health_url"], "snapshot health URL")
        https(snapshot["provider"]["endpoint"], "snapshot endpoint")
        require(len(snapshot["indicators"]) == 3, "expected three verified macro indicators")
        for indicator in snapshot["indicators"]:
            require(indicator.get("is_forecast") is False, f"{indicator.get('id')}: forecasts excluded")
            https(indicator.get("source_url"), f"{indicator.get('id')}: source URL")

        territory = load("qazgeo-public-snapshot.v1.json")
        require(territory["schema_version"] == "qaz-industries-qazgeo-public-snapshot-v1", "territory schema")
        require(territory["status"] == "ready", "territory snapshot must state ready")
        territory_retrieved_at = datetime.fromisoformat(territory["retrieved_at"].replace("Z", "+00:00"))
        territory_age_days = (datetime.now(timezone.utc) - territory_retrieved_at).days
        require(0 <= territory_age_days <= 31, f"territory snapshot is stale ({territory_age_days} days); refresh before release")
        https(territory["provider"]["health_url"], "territory health URL")
        https(territory["provider"]["layer_registry_url"], "territory layer registry URL")
        https(territory["provider"]["geojson_url"], "territory GeoJSON URL")
        for key in ("regions", "cities", "pois"):
            require(isinstance(territory["coverage"].get(key), int) and territory["coverage"][key] > 0, f"territory {key}")
        require(len(territory["public_layers"]) >= 1, "territory public layers")
        for layer in territory["public_layers"]:
            https(layer.get("url"), f"territory layer {layer.get('id')}")
        map_contract = territory.get("map_contract") or {}
        require(map_contract.get("schema_version") == "qaz-industries-qazgeo-regions-public-v1", "QazGeo map schema")
        require(map_contract.get("asset") == "data/qazgeo-regions-public.v1.geojson", "QazGeo map asset")
        https(map_contract.get("source_url"), "QazGeo map source URL")
        require(map_contract["source_url"] == territory["provider"]["geojson_url"], "QazGeo map source mismatch")
        require(map_contract.get("feature_count") == 20, "QazGeo map feature count")
        map_asset = load("qazgeo-regions-public.v1.geojson")
        require(map_asset.get("type") == "FeatureCollection", "QazGeo map FeatureCollection")
        require(map_asset.get("qaz_schema_version") == map_contract["schema_version"], "QazGeo map asset schema")
        require(len(map_asset.get("features", [])) == 20, "QazGeo map asset regions")
        safe_keys = {"code", "name_ru", "name_en", "region_type"}
        for feature in map_asset["features"]:
            require(feature.get("geometry", {}).get("type") in {"Polygon", "MultiPolygon"}, "QazGeo map geometry")
            require(set(feature.get("properties", {})) == safe_keys, "QazGeo map exposes only reviewed identity fields")
            require(isinstance(feature["properties"].get("code"), str), "QazGeo map region code")

        layer_registry = load("qazgeo-public-layer-registry.v1.json")
        require(layer_registry["schema_version"] == "qaz-industries-qazgeo-public-layer-registry-v1", "QazGeo layer registry schema")
        require(layer_registry["status"] == "ready", "QazGeo layer registry must state ready")
        layer_registry_retrieved_at = datetime.fromisoformat(layer_registry["retrieved_at"].replace("Z", "+00:00"))
        layer_registry_age_days = (datetime.now(timezone.utc) - layer_registry_retrieved_at).days
        require(0 <= layer_registry_age_days <= 31, f"QazGeo layer registry is stale ({layer_registry_age_days} days); refresh before release")
        provider = layer_registry["provider"]
        require(provider.get("service") == "qazgeo", "QazGeo layer registry provider")
        https(provider.get("health_url"), "QazGeo layer registry health URL")
        https(provider.get("layer_registry_url"), "QazGeo layer registry URL")
        layer_ids = {"regions", "infrastructure", "national_transport_network", "national_place_nodes", "hydro_stations", "water_objects_catalog"}
        require({layer.get("id") for layer in layer_registry["layers"]} == layer_ids, "QazGeo curated layer set")
        for layer in layer_registry["layers"]:
            require(layer.get("status") in {"stable", "beta"}, f"QazGeo layer {layer.get('id')}: status")
            require(layer.get("public_allowed") is True, f"QazGeo layer {layer.get('id')}: public policy")
            require(layer.get("dataset_status") in {"versioned_snapshot", "observed_snapshot", "contract_only"}, f"QazGeo layer {layer.get('id')}: dataset status")
            https(layer.get("contract_url"), f"QazGeo layer {layer.get('id')}: contract URL")
            https(layer.get("source_url"), f"QazGeo layer {layer.get('id')}: source URL")
            require(layer.get("contract"), f"QazGeo layer {layer.get('id')}: contract")
            require(isinstance(layer.get("public_projection"), list) and layer["public_projection"], f"QazGeo layer {layer.get('id')}: projection")
            require(isinstance(layer.get("coverage"), dict), f"QazGeo layer {layer.get('id')}: coverage")
            require(isinstance(layer.get("limitations"), str) and layer["limitations"], f"QazGeo layer {layer.get('id')}: limitations")

        registry = load("reviewed-source-registry.v1.json")
        require(registry["schema_version"] == "qazstack-reviewed-source-registry-v1", "registry schema")
        require(registry["source_count"] == len(registry["sources"]), "registry source count")
        require(registry["policy"]["private_materials_are_excluded"] is True, "private exclusion")
        for source in registry["sources"]:
            https(source.get("url"), f"source {source.get('id')}")
            require(source.get("rights_decision") == "approved-link-metadata", f"source {source.get('id')}: rights")

        editorial_ledger = load("edpol-editorial-ledger.v1.json")
        require(editorial_ledger["schema_version"] == "qaz-industries-edpol-editorial-ledger-v1", "EdPol editorial ledger schema")
        require(editorial_ledger["product_id"] == "qaz-industries", "EdPol editorial ledger product")
        require(editorial_ledger["status"] == "review-required", "EdPol editorial ledger must stay fail-closed")
        editorial_integration = editorial_ledger["integration"]
        require(editorial_integration["mode"] == "local-static-fail-closed", "EdPol editorial mode")
        require(editorial_integration["stores_content_bodies"] is False, "EdPol content body boundary")
        require(editorial_integration["writes_edpol_production"] is False, "EdPol production write boundary")
        require(editorial_integration["automatic_publication"] is False, "EdPol automatic publication boundary")
        for field in ("control_plane", "risk_register", "source_check", "article_trust_schema"):
            https(editorial_integration.get(field), f"EdPol {field}")
        require({item["source_id"] for item in editorial_ledger["source_reviews"]} == {item["id"] for item in registry["sources"]}, "EdPol source review scope")
        require(all(item["status"] == "review-required" for item in editorial_ledger["source_reviews"]), "EdPol source review status")
        require(len(editorial_ledger["materials"]) == 6 and all(item["decision"] == "needs-review" for item in editorial_ledger["materials"]), "EdPol material review status")
        require(editorial_ledger["corrections"]["status"] == "not-established", "EdPol corrections status")

        portfolio = load("portfolio-integration-registry.v1.json")
        require(
            portfolio["schema_version"] == "qaz-industries-portfolio-integration-registry-v1",
            "portfolio integration registry schema",
        )
        require(portfolio["product_id"] == "qaz-industries", "portfolio integration product")
        integrations = portfolio.get("integrations")
        require(isinstance(integrations, list) and len(integrations) == portfolio["measurement"]["scoped_surfaces"], "portfolio integration scope")
        statuses = [item.get("status") for item in integrations]
        require(statuses.count("source-verified") == portfolio["measurement"]["local_contract_backed"], "portfolio local contract count")
        require(statuses.count("public-snapshot-verified") == portfolio["measurement"]["public_snapshot_backed"], "portfolio snapshot count")
        require(statuses.count("public-contract-observed") == portfolio["measurement"]["public_contract_observed_link_only"], "portfolio link-only count")
        require(statuses.count("public-observed-no-registration") == portfolio["measurement"]["observed_without_registration"], "portfolio registration count")
        require(
            portfolio["measurement"]["reviewed_contract_or_snapshot_backed"]
            == portfolio["measurement"]["local_contract_backed"] + portfolio["measurement"]["public_snapshot_backed"],
            "portfolio reviewed contract count",
        )
        seen_integration_ids: set[str] = set()
        for integration in integrations:
            integration_id = integration.get("id")
            require(isinstance(integration_id, str) and integration_id not in seen_integration_ids, f"portfolio integration id: {integration_id}")
            seen_integration_ids.add(integration_id)
            require(isinstance(integration.get("name"), str) and integration["name"], f"portfolio integration {integration_id}: name")
            require(isinstance(integration.get("relationship"), str) and integration["relationship"], f"portfolio integration {integration_id}: relationship")
            require(integration.get("status") in {"source-verified", "public-snapshot-verified", "public-contract-observed", "public-observed-no-registration"}, f"portfolio integration {integration_id}: status")
            if integration.get("provider_url") is not None:
                https(integration["provider_url"], f"portfolio integration {integration_id}: provider URL")
            evidence = integration.get("evidence")
            require(isinstance(evidence, list) and evidence, f"portfolio integration {integration_id}: evidence")
            for item in evidence:
                require(isinstance(item, dict), f"portfolio integration {integration_id}: evidence item")
                if item.get("url") is not None:
                    https(item["url"], f"portfolio integration {integration_id}: evidence URL")
                if item.get("path") is not None:
                    require((ROOT / item["path"]).is_file(), f"portfolio integration {integration_id}: evidence path")
        boundaries = portfolio.get("boundaries")
        require(boundaries.get("direct_upstream_browser_access") is False, "portfolio direct upstream browser gate")
        require(boundaries.get("external_runtime_data_calls") is False, "portfolio external runtime data gate")
        require(boundaries.get("link_metadata_is_not_runtime_integration") is True, "portfolio link metadata boundary")

        manifest = json.loads((ROOT / "qazstack-thematic-product.json").read_text(encoding="utf-8"))
        require(manifest["schema_version"] == "qazstack-thematic-product-v1", "thematic manifest schema")
        require(manifest["publication"]["public_records_require_review"] is True, "review gate")
        require(manifest["publication"].get("edpol_editorial_ledger") == "data/edpol-editorial-ledger.v1.json", "EdPol ledger publication link")
        require(manifest["publication"].get("automatic_publication") is False, "EdPol automatic publication gate")
        require(manifest["geo_policy"]["private_browser_access_forbidden"] is True, "private geo browser gate")

        consumer = json.loads((ROOT / "qazstack-consumer.json").read_text(encoding="utf-8"))
        require(consumer["schema_version"] == "qazstack-consumer-contract-v1", "consumer contract schema")
        require(consumer.get("product_id") == manifest["product_id"], "consumer product identity")
        require(consumer.get("manifest_path") == "qazstack-thematic-product.json", "consumer manifest path")
        portfolio_contract = consumer.get("portfolio_integration_registry") or {}
        require(portfolio_contract.get("contract") == "qaz-industries-portfolio-integration-registry-v1", "consumer portfolio registry contract")
        require(portfolio_contract.get("asset") == "data/portfolio-integration-registry.v1.json", "consumer portfolio registry asset")
        require(portfolio_contract.get("link_only_is_not_runtime") is True, "consumer portfolio link-only boundary")
        require((ROOT / portfolio_contract["asset"]).is_file(), "consumer portfolio registry asset missing")
        editorial_contract = consumer.get("edpol_editorial_ledger") or {}
        require(editorial_contract.get("contract") == "qaz-industries-edpol-editorial-ledger-v1", "consumer EdPol editorial ledger contract")
        require(editorial_contract.get("asset") == "data/edpol-editorial-ledger.v1.json", "consumer EdPol editorial ledger asset")
        require(editorial_contract.get("mode") == "local-static-fail-closed", "consumer EdPol editorial ledger mode")
        require(editorial_contract.get("writes_edpol_production") is False, "consumer EdPol editorial write boundary")
        require((ROOT / editorial_contract["asset"]).is_file(), "consumer EdPol editorial ledger asset missing")
        require(consumer["runtime"].get("direct_upstream_browser_access") is False, "consumer direct upstream gate")
        https(consumer["runtime"].get("public_origin"), "consumer public origin")
        manifest_modules = {module["id"] for module in manifest["modules"]}
        consumer_modules = {module["id"] for module in consumer["modules"]}
        require(consumer_modules == manifest_modules, "consumer module set differs from manifest")
        for module in consumer["modules"]:
            asset = ROOT / module["asset"]
            require(asset.is_file(), f"consumer module {module['id']}: asset missing")
            if module.get("map_asset"):
                require((ROOT / module["map_asset"]).is_file(), f"consumer module {module['id']}: map asset missing")
            require(isinstance(module.get("allowed_states"), list) and module["allowed_states"], f"consumer module {module['id']}: states")
        for upstream in consumer["upstreams"]:
            if upstream.get("origin"):
                https(upstream["origin"], f"consumer upstream {upstream['id']}")
            for origin in upstream.get("origins", []):
                https(origin, f"consumer upstream {upstream['id']}")
        boundaries = consumer["boundaries"]
        require(boundaries.get("same_origin_assets_only") is True, "consumer same-origin gate")
        require(boundaries.get("contract_only_is_observation") is False, "consumer contract-only gate")

        avds = load("avds-coverage.v1.json")
        require(avds["schema_version"] == "qaz-industries-avds-coverage-v1", "AVDS coverage schema")
        require(avds["product_id"] == "qaz-industries", "AVDS coverage product")
        require(avds["method"]["kind"] == "avds-system-contract-categories", "AVDS coverage method")
        require(avds["method"]["passed"] == 128 and avds["method"]["total"] == 128, "AVDS system coverage counts")
        require(avds["coverage_percent"] == 100, "AVDS system coverage percentage")
        require(avds["badge"] == "AVDS 4.6.0-100", "AVDS coverage badge")
        require(avds["route_contract"]["passed"] == 12 and avds["route_contract"]["total"] == 12, "AVDS route coverage counts")
        require(avds["route_contract"]["coverage_percent"] == 100, "AVDS route coverage percentage")
        require(avds["system_contract"] == "data/avds-system-contract.v1.json", "AVDS system contract link")
        require(len(avds["dimensions"]) == 10, "AVDS system dimensions")
        https(avds["avds"]["source"], "AVDS source")

        avds_system = load("avds-system-contract.v1.json")
        require(avds_system["schema_version"] == "qaz-industries-avds-system-contract-v1", "AVDS system contract schema")
        require(avds_system["product_id"] == "qaz-industries", "AVDS system contract product")
        require(len(avds_system["categories"]) == 10, "AVDS system category count")
        require(len(avds_system["themes"]) == 6, "AVDS system theme matrix")
        require(all(theme.get("status") == "verified" and theme.get("selector") for theme in avds_system["themes"]), "AVDS theme implementations")

        locale_contract = json.loads((ROOT / "content" / "locale-contract.v1.json").read_text(encoding="utf-8"))
        require(locale_contract["schema_version"] == "qaz-industries-locale-contract-v1", "locale contract schema")
        icon_catalog = json.loads((ROOT / "data" / "avds-icon-catalog.v1.json").read_text(encoding="utf-8"))
        require(icon_catalog["schema_version"] == "qaz-industries-avds-icon-catalog-v1", "icon catalog schema")
        viz_contract = json.loads((ROOT / "data" / "avds-data-visualization-contract.v1.json").read_text(encoding="utf-8"))
        require(viz_contract["schema_version"] == "qaz-industries-avds-data-visualization-contract-v1", "visualization contract schema")
        accessibility_contract = json.loads((ROOT / "data" / "avds-accessibility-contract.v1.json").read_text(encoding="utf-8"))
        require(accessibility_contract["schema_version"] == "qaz-industries-avds-accessibility-contract-v1", "accessibility contract schema")
        require(accessibility_contract["acceptance"]["status"] == "verified", "screen-reader acceptance")
        zoom_proof = json.loads((ROOT / "data" / "avds-zoom-proof.v1.json").read_text(encoding="utf-8"))
        require(zoom_proof["schema_version"] == "qaz-industries-avds-zoom-proof-v1", "zoom proof schema")
        require(zoom_proof["acceptance"]["status"] == "verified" and all(item["overflow_free"] for item in zoom_proof["routes"]), "zoom acceptance")
        visual_contract = json.loads((ROOT / "data" / "avds-visual-regression.v1.json").read_text(encoding="utf-8"))
        require(visual_contract["schema_version"] == "qaz-industries-avds-visual-regression-v1", "visual regression schema")
        require(visual_contract["acceptance"]["status"] == "verified" and len(visual_contract["baselines"]) == 8, "visual regression acceptance")

        avds_responsive = load("avds-responsive-contract.v1.json")
        require(avds_responsive["schema_version"] == "qaz-industries-avds-responsive-contract-v1", "AVDS responsive contract schema")
        require(len(avds_responsive["viewports"]) == 8, "AVDS responsive viewport matrix")
        avds_route_ledger = load("avds-route-ledger.v1.json")
        require(avds_route_ledger["schema_version"] == "qaz-industries-avds-route-ledger-v1", "AVDS route ledger schema")
        require(len(avds_route_ledger["routes"]) == 4, "AVDS route ledger routes")

        avds_consumer = json.loads((ROOT / "avds-consumer.json").read_text(encoding="utf-8"))
        require(avds_consumer["schema_version"] == "qaz-industries-avds-consumer-v1", "AVDS consumer schema")
        require(avds_consumer["product_id"] == "qaz-industries", "AVDS consumer product")
        require(avds_consumer["integration_mode"] == "static-contract", "AVDS consumer integration mode")
        require(avds_consumer["avds_version"] == avds["avds"]["version"], "AVDS consumer version")
        require(avds_consumer["adoption"]["package_runtime"] is True, "AVDS package runtime claim")
        require(avds_consumer["adoption"]["package_runtime_receipt"] == "data/avds-package-runtime.v1.json", "AVDS package runtime receipt")
        require(avds_consumer["catalog_registration"]["consumer_id"] == "qaz_industries", "AVDS catalog consumer id")
        require(avds_consumer["catalog_registration"]["state"] == "source-registered", "AVDS catalog registration")
        https(avds_consumer["canonical_url"], "AVDS consumer canonical URL")
        https(avds_consumer["source_repository"], "AVDS consumer source repository")
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"public contract: FAILED: {error}")
        return 1
    print("public contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
