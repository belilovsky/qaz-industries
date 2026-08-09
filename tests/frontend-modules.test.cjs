const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const contracts = require('../snapshot-contracts.js');
const geometry = require('../qazgeo-geometry.js');
const profileView = require('../profile-view.js');

function readJson(filename) {
  return JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', filename), 'utf8'));
}

test('reviewed snapshot contracts accept every shipped public projection', () => {
  assert.equal(contracts.validateQazLake(readJson('qazlake-public-snapshot.v1.json')), true);
  assert.equal(contracts.validateQazGeoSummary(readJson('qazgeo-public-snapshot.v1.json')), true);
  assert.equal(contracts.validateLayerRegistry(readJson('qazgeo-public-layer-registry.v1.json')), true);
  assert.equal(contracts.validateRegionsGeoJson(readJson('qazgeo-regions-public.v1.geojson')), true);
});

test('reviewed contracts reject private transport and invented observations', () => {
  assert.equal(contracts.isHttps('https://qgeo.tech/tiles/regions'), true);
  assert.equal(contracts.isHttps('http://qgeo.tech/tiles/regions'), false);
  const registry = readJson('qazgeo-public-layer-registry.v1.json');
  registry.layers[0].public_allowed = false;
  assert.throws(() => contracts.validateLayerRegistry(registry), /is not public/);
});

test('QazGeo geometry builds one finite SVG path per reviewed region', () => {
  const payload = readJson('qazgeo-regions-public.v1.geojson');
  const model = geometry.buildModel(payload, 'https://qgeo.tech/');
  assert.equal(model.features.length, 20);
  assert.equal(new Set(model.features.map((feature) => feature.id)).size, 20);
  model.features.forEach((feature) => {
    assert.match(feature.path, /^M /);
    assert.match(feature.path, / Z$/);
    assert.equal(/NaN|Infinity/.test(feature.path), false);
  });
});

test('QazGeo geometry fails closed on unsupported shapes', () => {
  assert.throws(
    () => geometry.pathForGeometry({ type: 'Point', coordinates: [1, 2] }, {}),
    /Unsupported QazGeo geometry/,
  );
});

test('profile view exposes deterministic Russian labels and coverage guards', () => {
  assert.equal(profileView.statusLabel('ready'), 'Готово');
  assert.equal(profileView.statusLabel('partial'), 'Частично');
  assert.equal(profileView.layerStatusLabel({ dataset_status: 'contract_only' }), 'только контракт');
  assert.equal(profileView.licenseStatusLabel('documented'), 'условия описаны');
  assert.equal(profileView.licenseStatusLabel('attribution-required'), 'требуется атрибуция');
  assert.equal(profileView.layerCoverageLabel({ scope: 'Казахстан', geographies: 20 }), 'Казахстан · 20 географий');
  assert.throws(() => profileView.coverageState('unknown'), /Unsupported coverage state/);
});
