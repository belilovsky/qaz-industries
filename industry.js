const profiles = window.QAZ_INDUSTRIES;
const profileKeys = Object.keys(profiles);
const coverageStates = new Set(['ready', 'partial', 'gap']);
let activeProfile = profiles.energy;
let publicSnapshot = null;

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

function snapshotAssetUrl() {
  const version = encodeURIComponent(window.QAZ_INDUSTRIES_ASSET_VERSION || 'source');
  return `data/qazlake-public-snapshot.v1.json?v=${version}`;
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
    boundary.textContent = 'Региональные и водные контракты не подключены без подтверждённого public endpoint.';
    return;
  }
  const provider = publicSnapshot.provider;
  status.innerHTML = `Проверенный static snapshot · ${escapeHtml(provider.service)} · revision ${escapeHtml(provider.source_revision)} · получен ${escapeHtml(dateLabel(publicSnapshot.retrieved_at.slice(0, 10)))}.`;
  grid.innerHTML = publicSnapshot.indicators.map((item) => `
    <article>
      <span>${escapeHtml(item.label)}</span>
      <strong>${escapeHtml(String(item.value).replace('.', ','))}<small>${escapeHtml(item.unit)}</small></strong>
      <p>на ${escapeHtml(dateLabel(item.as_of))} · <a href="${externalUrl(item.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(item.source)} ↗</a></p>
    </article>
  `).join('');
  const unavailable = publicSnapshot.unavailable_modules.map((item) => item.reason).join(' ');
  boundary.textContent = unavailable || 'Публичный региональный слой проверен отдельно перед включением.';
}

async function loadPublicSnapshot() {
  try {
    const response = await fetch(snapshotAssetUrl(), { cache: 'no-store' });
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
    <article><strong>${escapeHtml(item.value)}</strong><span>${escapeHtml(item.label)}</span><small>${escapeHtml(item.period)}</small></article>
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
    <article><span>0${index + 1}</span><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.text)}</p></article>
  `).join('');

  document.querySelector('#geography-grid').innerHTML = profile.geography.map((item) => `
    <article><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.text)}</p></article>
  `).join('');

  document.querySelector('#coverage-list').innerHTML = Object.entries(profile.coverage).map(([label, status]) => `
    <div><strong>${escapeHtml(label)}</strong><span class="coverage-state state-${coverageState(status)}">${statusLabel(status)}</span></div>
  `).join('');

  document.querySelector('#gap-list').innerHTML = profile.gaps.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  document.querySelector('#source-links').innerHTML = profile.sources.map((item, index) => `
    <a href="${externalUrl(item.url)}" target="_blank" rel="noreferrer"><span>0${index + 1}</span><strong>${escapeHtml(item.label)}</strong><b>↗</b></a>
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
