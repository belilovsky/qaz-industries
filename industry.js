const profiles = window.QAZ_INDUSTRIES;
const profileKeys = Object.keys(profiles);
const coverageStates = new Set(['ready', 'partial', 'gap']);
let activeProfile = profiles.energy;
let publicSnapshot = null;
let territorySnapshot = null;
let layerRegistry = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
}

function externalUrl(value) {
  const url = new URL(value);
  if (url.protocol !== 'https:') throw new Error(`Unsupported external URL: ${value}`);
  return escapeHtml(url.href);
}

function coverageState(value) {
  if (!coverageStates.has(value)) throw new Error(`Unsupported coverage state: ${value}`);
  return value;
}

function statusLabel(status) {
  return status === 'ready' ? 'Готово' : status === 'partial' ? 'Частично' : 'Пробел';
}

function dateLabel(value) {
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'
  }).format(date);
}

function snapshotAssetUrl(filename) {
  const version = encodeURIComponent(window.QAZ_INDUSTRIES_ASSET_VERSION || 'source');
  return `data/${filename}?v=${version}`;
}

function renderPassport(profile) {
  document.querySelector('#passport-source').textContent = profile.sourceName;
  document.querySelector('#passport-release').textContent = profile.release;
  document.querySelector('#profile-machine-link').setAttribute('aria-label', `Открыть JSON профилей; выбран ${profile.name}`);
}

function renderPulse() {
  const status = document.querySelector('#pulse-status');
  const grid = document.querySelector('#pulse-grid');
  const boundary = document.querySelector('#pulse-boundary-state');
  if (!publicSnapshot) {
    status.textContent = 'Публичный QazLake snapshot недоступен. Отраслевой профиль продолжает работать без него.';
    grid.innerHTML = '';
  } else {
    const provider = publicSnapshot.provider;
    status.innerHTML = `Проверенный static snapshot · ${escapeHtml(provider.service)} · revision ${escapeHtml(provider.source_revision)} · получен ${escapeHtml(dateLabel(publicSnapshot.retrieved_at.slice(0, 10)))}.`;
    grid.innerHTML = publicSnapshot.indicators.map((item) => `
      <article class="av-card av-card--outlined">
        <span>${escapeHtml(item.label)}</span>
        <strong>${escapeHtml(String(item.value).replace('.', ','))}<small>${escapeHtml(item.unit)}</small></strong>
        <p>на ${escapeHtml(dateLabel(item.as_of))} · <a href="${externalUrl(item.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(item.source)} ↗</a></p>
      </article>
    `).join('');
  }
  renderTerritory();
  const unavailable = [
    ...(publicSnapshot?.unavailable_modules || []),
    ...(territorySnapshot?.unavailable_modules || []),
  ].map((item) => item.reason).join(' ');
  boundary.textContent = unavailable || 'Публичные контракты QazLake и QazGeo проверены отдельно перед включением.';
}

function renderTerritory() {
  const status = document.querySelector('#territory-status');
  const grid = document.querySelector('#territory-grid');
  if (!territorySnapshot) {
    status.textContent = 'Публичный QazGeo snapshot недоступен. География профиля остаётся обзорной и не получает непроверенные значения.';
    grid.innerHTML = '';
    return;
  }
  const provider = territorySnapshot.provider;
  status.textContent = `Проверенный static snapshot · ${provider.service} · revision ${provider.source_revision} · получен ${dateLabel(territorySnapshot.retrieved_at.slice(0, 10))}.`;
  const cards = [
    ['Регионов', territorySnapshot.coverage.regions, 'национальная территориальная основа'],
    ['Городов', territorySnapshot.coverage.cities, 'публичный географический каталог'],
    ['Точек интереса', territorySnapshot.coverage.pois, 'без передачи точных координат в QAZ'],
  ];
  grid.innerHTML = cards.map(([label, value, note]) => `
    <article class="av-card av-card--outlined"><span>${escapeHtml(label)}</span><strong>${escapeHtml(Number(value).toLocaleString('ru-RU'))}</strong><p>${escapeHtml(note)}</p></article>
  `).join('');
}

function layerStatusLabel(layer) {
  if (layer.dataset_status === 'contract_only') return 'contract-only';
  if (layer.status === 'stable') return 'stable layer';
  return 'reviewed beta';
}

function layerCoverageLabel(coverage) {
  if (!coverage || typeof coverage !== 'object') return 'Покрытие уточняется';
  const parts = [];
  if (coverage.scope) parts.push(String(coverage.scope));
  if (coverage.geographies === null || coverage.status === 'unknown') parts.push('объём не наблюдался');
  if (Number.isFinite(coverage.geographies)) parts.push(`${Number(coverage.geographies).toLocaleString('ru-RU')} географий`);
  if (Number.isFinite(coverage.segments)) parts.push(`${Number(coverage.segments).toLocaleString('ru-RU')} сегментов`);
  if (Number.isFinite(coverage.features)) parts.push(`${Number(coverage.features).toLocaleString('ru-RU')} объектов`);
  return parts.join(' · ') || 'Покрытие уточняется';
}

function layerFreshnessLabel(layer) {
  const freshness = layer.freshness || {};
  if (!freshness.data_updated_at) return 'Наблюдение не заявлено';
  return `данные на ${dateLabel(freshness.data_updated_at)}`;
}

function renderLayerRegistry() {
  const status = document.querySelector('#layer-registry-status');
  const grid = document.querySelector('#layer-registry-grid');
  if (!status || !grid) return;
  if (!layerRegistry) {
    status.textContent = 'Публичный QazGeo layer registry недоступен. Значения слоёв не подставляются без reviewed snapshot.';
    grid.innerHTML = '';
    return;
  }
  const provider = layerRegistry.provider;
  const contractOnlyCount = layerRegistry.layers.filter((layer) => layer.dataset_status === 'contract_only').length;
  status.textContent = `Reviewed layer registry · ${provider.service} · revision ${provider.source_revision} · ${layerRegistry.layers.length} контрактов; ${contractOnlyCount} пока только roadmap.`;
  grid.innerHTML = layerRegistry.layers.map((layer, index) => {
    const badgeClass = layer.dataset_status === 'contract_only' ? 'av-badge--info' : 'av-badge--success';
    const freshness = layerFreshnessLabel(layer);
    return `
      <article class="av-card av-card--outlined av-layer-registry__card">
        <div class="av-layer-registry__body">
          <div class="av-layer-registry__title-row">
            <div class="av-layer-registry__header">
              <p class="av-layer-registry__eyebrow">0${index + 1} · ${escapeHtml(layer.kind)}</p>
              <h3>${escapeHtml(layer.title)}</h3>
            </div>
            <span class="av-badge ${badgeClass}">${escapeHtml(layerStatusLabel(layer))}</span>
          </div>
          <p class="av-layer-registry__description">${escapeHtml(layer.description)}</p>
          <dl class="av-layer-registry__metadata">
            <div class="av-layer-registry__metadata-row"><dt>Покрытие</dt><dd>${escapeHtml(layerCoverageLabel(layer.coverage))}</dd></div>
            <div class="av-layer-registry__metadata-row"><dt>Свежесть</dt><dd>${escapeHtml(freshness)}</dd></div>
            <div class="av-layer-registry__metadata-row"><dt>Лицензия</dt><dd>${escapeHtml(layer.license?.status || 'reviewed')} · ${escapeHtml(layer.provenance?.attribution || 'QazGeo')}</dd></div>
          </dl>
          <p class="av-layer-registry__limit">${escapeHtml(layer.limitations)}</p>
          <div class="av-layer-registry__actions"><a class="av-layer-registry__action" href="${externalUrl(layer.contract_url)}" target="_blank" rel="noreferrer">Открыть контракт ↗</a><a class="av-layer-registry__source" href="${externalUrl(layer.source_url)}" target="_blank" rel="noreferrer">Источник ↗</a></div>
        </div>
      </article>
    `;
  }).join('');
}

async function loadPublicSnapshot() {
  try {
    const response = await fetch(snapshotAssetUrl('qazlake-public-snapshot.v1.json'), { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const snapshot = await response.json();
    if (snapshot.schema_version !== 'qaz-industries-qazlake-public-snapshot-v1' || snapshot.status !== 'ready') {
      throw new Error('unexpected public snapshot contract');
    }
    publicSnapshot = snapshot;
  } catch (error) {
    console.warn('QazLake public snapshot unavailable:', error);
  }
  renderPulse(activeProfile);
}

async function loadTerritorySnapshot() {
  try {
    const response = await fetch(snapshotAssetUrl('qazgeo-public-snapshot.v1.json'), { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const snapshot = await response.json();
    if (snapshot.schema_version !== 'qaz-industries-qazgeo-public-snapshot-v1' || snapshot.status !== 'ready') {
      throw new Error('unexpected territory snapshot contract');
    }
    if (![snapshot.coverage?.regions, snapshot.coverage?.cities, snapshot.coverage?.pois].every(Number.isFinite)) {
      throw new Error('invalid territory coverage');
    }
    territorySnapshot = snapshot;
  } catch (error) {
    console.warn('QazGeo public snapshot unavailable:', error);
  }
  renderPulse(activeProfile);
}

async function loadLayerRegistry() {
  try {
    const response = await fetch(snapshotAssetUrl('qazgeo-public-layer-registry.v1.json'), { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const snapshot = await response.json();
    if (snapshot.schema_version !== 'qaz-industries-qazgeo-public-layer-registry-v1' || snapshot.status !== 'ready') {
      throw new Error('unexpected QazGeo layer registry contract');
    }
    if (!Array.isArray(snapshot.layers) || snapshot.layers.length < 1 || snapshot.provider?.service !== 'qazgeo') {
      throw new Error('invalid QazGeo layer registry payload');
    }
    layerRegistry = snapshot;
  } catch (error) {
    console.warn('QazGeo public layer registry unavailable:', error);
  }
  renderLayerRegistry();
}

function renderProfile(key, updateUrl = true) {
  const profile = profiles[key] || profiles.energy;
  activeProfile = profile;
  document.title = `${profile.name} — QAZ.INDUSTRIES`;
  document.querySelector('#toolbar-current').textContent = profile.name;
  document.querySelector('#profile-code').textContent = profile.code;
  document.querySelector('#profile-title').textContent = profile.name;
  document.querySelector('#profile-summary').textContent = profile.summary;
  document.querySelector('#profile-status').textContent = profile.status;
  document.querySelector('#profile-release').textContent = profile.release;
  document.querySelector('#profile-about').textContent = profile.about;
  document.querySelector('#profile-evidence-source').textContent = profile.sourceName;
  document.querySelector('#profile-evidence-release').textContent = profile.release;
  const evidenceLink = document.querySelector('#profile-evidence-link');
  evidenceLink.href = externalUrl(profile.sourceUrl);
  evidenceLink.textContent = 'Проверить ' + profile.sourceName + ' ↗';
  const sourceTop = document.querySelector('#profile-source-top');
  sourceTop.href = externalUrl(profile.sourceUrl);
  sourceTop.textContent = `${profile.sourceName} ↗`;
  renderPassport(profile);
  renderPulse();

  document.querySelectorAll('[data-sector]').forEach((button) => {
    const active = button.dataset.sector === profile.id;
    button.setAttribute('aria-pressed', String(active));
    button.classList.toggle('is-active', active);
  });

  document.querySelector('#profile-kpis').innerHTML = profile.kpis.map((item) => `
    <article class="av-card av-card--outlined"><strong>${escapeHtml(item.value)}</strong><span>${escapeHtml(item.label)}</span><small>${escapeHtml(item.period)}</small></article>
  `).join('');

  document.querySelector('#indicator-rows').innerHTML = profile.indicators.map((item) => `
    <div class="indicator-row" role="row">
      <strong role="cell">${escapeHtml(item.name)}</strong>
      <span class="indicator-value" role="cell">${escapeHtml(item.value)} <small>${escapeHtml(item.unit)}</small></span>
      <span role="cell">${escapeHtml(item.period)}</span>
      <span role="cell">${escapeHtml(item.note)}</span>
      <a role="cell" href="${externalUrl(item.url)}" target="_blank" rel="noreferrer">открыть ↗</a>
    </div>
  `).join('');

  document.querySelector('#chain-grid').innerHTML = profile.chain.map((item, index) => `
    <article class="av-card av-card--outlined"><span>0${index + 1}</span><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.text)}</p></article>
  `).join('');

  document.querySelector('#geography-grid').innerHTML = profile.geography.map((item) => `
    <article class="av-card av-card--outlined"><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.text)}</p></article>
  `).join('');

  document.querySelector('#coverage-list').innerHTML = Object.entries(profile.coverage).map(([label, status]) => `
    <div><strong>${escapeHtml(label)}</strong><span class="coverage-state state-${coverageState(status)}">${statusLabel(status)}</span></div>
  `).join('');

  document.querySelector('#gap-list').innerHTML = profile.gaps.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  document.querySelector('#source-links').innerHTML = profile.sources.map((item, index) => `
    <article class="av-card av-card--outlined av-source-registry__record">
      <div class="av-card__body av-source-registry__record-body">
        <div class="av-source-registry__title-row">
          <div class="av-source-registry__record-header">
            <p class="av-source-registry__record-eyebrow">0${index + 1} · REVIEWED SOURCE</p>
            <h3>${escapeHtml(item.label)}</h3>
          </div>
          <span class="av-badge av-badge--success">reviewed link</span>
        </div>
        <p class="av-source-registry__record-description">Публичный маршрут к ${escapeHtml(item.label.toLowerCase())}; QAZ показывает link metadata и не копирует исходный реестр.</p>
        <dl class="av-source-registry__metadata">
          <div class="av-source-registry__metadata-row"><dt>Продукт</dt><dd>${escapeHtml(profile.sourceName)}</dd></div>
          <div class="av-source-registry__metadata-row"><dt>Срез</dt><dd>${escapeHtml(profile.release)}</dd></div>
        </dl>
        <div class="av-source-registry__actions"><a class="av-source-registry__action" href="${externalUrl(item.url)}" target="_blank" rel="noreferrer">Открыть источник ↗</a></div>
      </div>
    </article>
  `).join('');

  if (updateUrl) {
    const next = new URL(window.location.href);
    next.searchParams.set('sector', profile.id);
    history.replaceState({}, '', next);
  }
}

function renderComparison() {
  const a = profiles[document.querySelector('#compare-a').value];
  const b = profiles[document.querySelector('#compare-b').value];
  const rows = Object.keys(a.coverage);
  document.querySelector('#compare-table').innerHTML = `
    <div class="compare-row compare-table-head"><span>Слой профиля</span><strong>${escapeHtml(a.short)}</strong><strong>${escapeHtml(b.short)}</strong></div>
    ${rows.map((label) => `
      <div class="compare-row"><span>${escapeHtml(label)}</span><strong class="state-${coverageState(a.coverage[label])}">${statusLabel(a.coverage[label])}</strong><strong class="state-${coverageState(b.coverage[label])}">${statusLabel(b.coverage[label])}</strong></div>
    `).join('')}
  `;
}

document.querySelectorAll('[data-sector]').forEach((button) => {
  button.addEventListener('click', () => renderProfile(button.dataset.sector));
});
document.querySelector('#compare-a')?.addEventListener('change', renderComparison);
document.querySelector('#compare-b')?.addEventListener('change', renderComparison);

const initialSector = new URLSearchParams(window.location.search).get('sector');
renderProfile(profileKeys.includes(initialSector) ? initialSector : 'energy', false);
renderComparison();
loadPublicSnapshot();
loadTerritorySnapshot();
renderLayerRegistry();
loadLayerRegistry();
