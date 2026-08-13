const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const contracts = require('../snapshot-contracts.js');
const geometry = require('../qazgeo-geometry.js');
const profileView = require('../profile-view.js');
const locale = require('../locale.js');

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

test('AVDS state and locale contracts fail closed', () => {
  assert.equal(locale.number(12345.678, { maximumFractionDigits: 2 }), '12 345,68');
  assert.equal(locale.unit(null, 'млн'), '—');
  assert.equal(locale.snapshotState('2026-08-01T00:00:00Z', Date.parse('2026-08-12T00:00:00Z')), 'success');
  assert.equal(locale.snapshotState('2026-06-01T00:00:00Z', Date.parse('2026-08-12T00:00:00Z')), 'stale');
  assert.equal(locale.snapshotState(null), 'empty');
  assert.match(profileView.stateCard('Нет данных', locale.message('offline'), 'offline'), /data-av-state="offline"/);
  assert.match(profileView.stateCard('Загрузка', locale.message('loading'), 'loading'), /av-skeleton/);
});

test('homepage filter summary keeps the complete locale template', async () => {
  const summary = { textContent: '' };
  const listeners = {};
  const buttons = ['all', 'infra'].map((filter) => ({
    dataset: { filter },
    classList: { toggle() {} },
    addEventListener(type, callback) { listeners[filter] = callback; },
    setAttribute() {},
    getAttribute(name) { return name === 'aria-pressed' && filter === 'all' ? 'true' : 'false'; },
  }));
  const cards = [
    { dataset: { kind: 'sector' }, hidden: false },
    { dataset: { kind: 'infra' }, hidden: false },
  ];
  const context = {
    document: {
      querySelectorAll(selector) {
        if (selector === '[data-filter]') return buttons;
        if (selector === '[data-kind]') return cards;
        return [];
      },
      querySelector(selector) {
        return selector === '#filter-summary' ? summary : null;
      },
    },
    QAZ_LOCALE: {
      t: () => 'Бағыттар: {visible} / {total}',
      onChange(callback) { context.localeChanged = callback; },
      loadCatalog: async () => ({}),
    },
  };
  context.globalThis = context;
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '..', 'app.js'), 'utf8'), context);
  await Promise.resolve();
  assert.equal(summary.textContent, 'Бағыттар: 2 / 2');
  listeners.infra();
  assert.equal(summary.textContent, 'Бағыттар: 1 / 2');
  context.localeChanged();
  assert.equal(summary.textContent, 'Бағыттар: 1 / 2');
});
