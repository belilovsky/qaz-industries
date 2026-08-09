(function () {
  'use strict';

  const profiles = window.QAZ_INDUSTRIES;
  const runtime = window.QAZ_RUNTIME;
  const contracts = window.QAZ_SNAPSHOT_CONTRACTS;
  const profileView = window.QAZ_PROFILE_VIEW;
  if (!profiles || !runtime || !contracts || !profileView) {
    throw new Error('QAZ profile dependencies are unavailable');
  }

  const profileKeys = Object.keys(profiles);
  const view = profileView.createProfileView(document, runtime);
  const snapshots = { public: null, territory: null, layers: null };
  let activeProfile = profiles.energy;

  function renderSnapshotModules() {
    view.renderPulse(snapshots.public, snapshots.territory);
    view.renderLayerRegistry(snapshots.layers);
  }

  function selectProfile(key, updateUrl = true) {
    activeProfile = profiles[key] || profiles.energy;
    view.renderProfile(activeProfile);
    view.renderPulse(snapshots.public, snapshots.territory);
    if (updateUrl) {
      const next = new URL(window.location.href);
      next.searchParams.set('sector', activeProfile.id);
      history.replaceState({}, '', next);
    }
  }

  function renderComparison() {
    const profileA = profiles[document.querySelector('#compare-a').value];
    const profileB = profiles[document.querySelector('#compare-b').value];
    view.renderComparison(profileA, profileB);
  }

  async function loadSnapshot({ path, validate, assign, label, render }) {
    try {
      assign(await runtime.fetchJsonAsset(path, { validate }));
    } catch (error) {
      console.warn(`${label} unavailable:`, error);
    }
    render();
  }

  document.querySelectorAll('[data-sector]').forEach((button) => {
    button.addEventListener('click', () => selectProfile(button.dataset.sector));
  });
  document.querySelector('#compare-a')?.addEventListener('change', renderComparison);
  document.querySelector('#compare-b')?.addEventListener('change', renderComparison);

  const initialSector = new URLSearchParams(window.location.search).get('sector');
  selectProfile(profileKeys.includes(initialSector) ? initialSector : 'energy', false);
  renderComparison();
  renderSnapshotModules();

  void Promise.all([
    loadSnapshot({
      path: 'data/qazlake-public-snapshot.v1.json',
      validate: contracts.validateQazLake,
      assign: (snapshot) => { snapshots.public = snapshot; },
      label: 'QazLake public snapshot',
      render: () => view.renderPulse(snapshots.public, snapshots.territory),
    }),
    loadSnapshot({
      path: 'data/qazgeo-public-snapshot.v1.json',
      validate: contracts.validateQazGeoSummary,
      assign: (snapshot) => { snapshots.territory = snapshot; },
      label: 'QazGeo public snapshot',
      render: () => view.renderPulse(snapshots.public, snapshots.territory),
    }),
    loadSnapshot({
      path: 'data/qazgeo-public-layer-registry.v1.json',
      validate: contracts.validateLayerRegistry,
      assign: (snapshot) => { snapshots.layers = snapshot; },
      label: 'QazGeo public layer registry',
      render: () => view.renderLayerRegistry(snapshots.layers),
    }),
  ]);
}());
