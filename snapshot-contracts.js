(function (root, factory) {
  'use strict';

  const contracts = Object.freeze(factory());
  if (typeof module === 'object' && module.exports) module.exports = contracts;
  if (root) root.QAZ_SNAPSHOT_CONTRACTS = contracts;
}(typeof globalThis === 'undefined' ? this : globalThis, function () {
  'use strict';

  const layerStates = new Set(['observed_snapshot', 'versioned_snapshot', 'contract_only']);

  function requireValue(condition, message) {
    if (!condition) throw new Error(message);
  }

  function isHttps(value) {
    try {
      const url = new URL(String(value));
      return url.protocol === 'https:' && !url.username && !url.password;
    } catch (_) {
      return false;
    }
  }

  function validateProvider(payload, expectedService) {
    requireValue(payload && typeof payload === 'object', 'snapshot must be an object');
    requireValue(payload.status === 'ready', 'snapshot status must be ready');
    requireValue(payload.provider && typeof payload.provider === 'object', 'snapshot provider is required');
    requireValue(String(payload.provider.service).startsWith(expectedService), `snapshot provider must be ${expectedService}`);
    requireValue(typeof payload.provider.source_revision === 'string' && payload.provider.source_revision.length > 0, 'source revision is required');
    requireValue(typeof payload.retrieved_at === 'string' && !Number.isNaN(Date.parse(payload.retrieved_at)), 'retrieved_at must be an ISO date');
    requireValue(String(payload.publication_mode).startsWith('reviewed-static-'), 'snapshot must use reviewed static publication mode');
  }

  function validateQazLake(payload) {
    validateProvider(payload, 'qazlake');
    requireValue(payload.schema_version === 'qaz-industries-qazlake-public-snapshot-v1', 'unexpected QazLake schema');
    requireValue(Array.isArray(payload.indicators) && payload.indicators.length > 0, 'QazLake indicators are required');
    payload.indicators.forEach((item) => {
      requireValue(item && typeof item.id === 'string' && item.id, 'QazLake indicator id is required');
      requireValue(typeof item.label === 'string' && item.label, `QazLake ${item.id} label is required`);
      requireValue(Number.isFinite(item.value), `QazLake ${item.id} value must be finite`);
      requireValue(typeof item.unit === 'string' && item.unit, `QazLake ${item.id} unit is required`);
      requireValue(/^\d{4}-\d{2}-\d{2}$/.test(item.as_of), `QazLake ${item.id} as_of is invalid`);
      requireValue(isHttps(item.source_url), `QazLake ${item.id} source URL must be public HTTPS`);
    });
    return true;
  }

  function validateQazGeoSummary(payload) {
    validateProvider(payload, 'qazgeo');
    requireValue(payload.schema_version === 'qaz-industries-qazgeo-public-snapshot-v1', 'unexpected QazGeo summary schema');
    requireValue([payload.coverage?.regions, payload.coverage?.cities, payload.coverage?.pois].every(Number.isFinite), 'QazGeo coverage must be finite');
    requireValue(payload.map_contract?.schema_version === 'qaz-industries-qazgeo-regions-public-v1', 'QazGeo map contract schema is invalid');
    requireValue(payload.map_contract?.feature_count === 20, 'QazGeo map contract must contain 20 regions');
    return true;
  }

  function validateLayerRegistry(payload) {
    validateProvider(payload, 'qazgeo');
    requireValue(payload.schema_version === 'qaz-industries-qazgeo-public-layer-registry-v1', 'unexpected QazGeo layer registry schema');
    requireValue(Array.isArray(payload.layers) && payload.layers.length > 0, 'QazGeo layers are required');
    payload.layers.forEach((layer) => {
      requireValue(layer && typeof layer.id === 'string' && layer.id, 'QazGeo layer id is required');
      requireValue(typeof layer.title === 'string' && layer.title, `QazGeo ${layer.id} title is required`);
      requireValue(layer.public_allowed === true, `QazGeo ${layer.id} is not public`);
      requireValue(layerStates.has(layer.dataset_status), `QazGeo ${layer.id} dataset status is invalid`);
      requireValue(isHttps(layer.contract_url) && isHttps(layer.source_url), `QazGeo ${layer.id} URLs must be public HTTPS`);
      requireValue(typeof layer.limitations === 'string' && layer.limitations, `QazGeo ${layer.id} limitations are required`);
    });
    return true;
  }

  function validateRegionsGeoJson(payload) {
    requireValue(payload && payload.type === 'FeatureCollection', 'QazGeo map must be a FeatureCollection');
    requireValue(payload.qaz_schema_version === 'qaz-industries-qazgeo-regions-public-v1', 'unexpected QazGeo map schema');
    requireValue(Array.isArray(payload.features) && payload.features.length === 20, 'QazGeo map must contain 20 regions');
    payload.features.forEach((feature) => {
      requireValue(feature?.properties?.code, 'QazGeo region code is required');
      requireValue(feature?.properties?.name_ru, `QazGeo ${feature?.properties?.code || 'region'} Russian name is required`);
      requireValue(['Polygon', 'MultiPolygon'].includes(feature?.geometry?.type), `QazGeo ${feature.properties.code} geometry is invalid`);
      requireValue(Array.isArray(feature.geometry.coordinates), `QazGeo ${feature.properties.code} coordinates are required`);
    });
    return true;
  }

  return {
    isHttps,
    validateLayerRegistry,
    validateQazGeoSummary,
    validateQazLake,
    validateRegionsGeoJson,
  };
}));
