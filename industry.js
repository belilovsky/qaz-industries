const profiles = window.QAZ_INDUSTRIES;
const profileKeys = Object.keys(profiles);

function statusLabel(status) {
  return status === 'ready' ? 'Готово' : status === 'partial' ? 'Частично' : 'Пробел';
}

function renderProfile(key, updateUrl = true) {
  const profile = profiles[key] || profiles.energy;
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
  evidenceLink.href = profile.sourceUrl;
  evidenceLink.textContent = 'Проверить ' + profile.sourceName + ' ↗';
  const sourceTop = document.querySelector('#profile-source-top');
  sourceTop.href = profile.sourceUrl;
  sourceTop.textContent = `${profile.sourceName} ↗`;

  document.querySelectorAll('[data-sector]').forEach((button) => {
    const active = button.dataset.sector === profile.id;
    button.setAttribute('aria-pressed', String(active));
    button.classList.toggle('is-active', active);
  });

  document.querySelector('#profile-kpis').innerHTML = profile.kpis.map((item) => `
    <article><strong>${item.value}</strong><span>${item.label}</span><small>${item.period}</small></article>
  `).join('');

  document.querySelector('#indicator-rows').innerHTML = profile.indicators.map((item) => `
    <div class="indicator-row" role="row">
      <strong role="cell">${item.name}</strong>
      <span class="indicator-value" role="cell">${item.value} <small>${item.unit}</small></span>
      <span role="cell">${item.period}</span>
      <span role="cell">${item.note}</span>
      <a role="cell" href="${item.url}" target="_blank" rel="noreferrer">открыть ↗</a>
    </div>
  `).join('');

  document.querySelector('#chain-grid').innerHTML = profile.chain.map((item, index) => `
    <article><span>0${index + 1}</span><strong>${item.title}</strong><p>${item.text}</p></article>
  `).join('');

  document.querySelector('#geography-grid').innerHTML = profile.geography.map((item) => `
    <article><strong>${item.title}</strong><p>${item.text}</p></article>
  `).join('');

  document.querySelector('#coverage-list').innerHTML = Object.entries(profile.coverage).map(([label, status]) => `
    <div><strong>${label}</strong><span class="coverage-state state-${status}">${statusLabel(status)}</span></div>
  `).join('');

  document.querySelector('#gap-list').innerHTML = profile.gaps.map((item) => `<li>${item}</li>`).join('');
  document.querySelector('#source-links').innerHTML = profile.sources.map((item, index) => `
    <a href="${item.url}" target="_blank" rel="noreferrer"><span>0${index + 1}</span><strong>${item.label}</strong><b>↗</b></a>
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
    <div class="compare-row compare-table-head"><span>Слой профиля</span><strong>${a.short}</strong><strong>${b.short}</strong></div>
    ${rows.map((label) => `
      <div class="compare-row"><span>${label}</span><strong class="state-${a.coverage[label]}">${statusLabel(a.coverage[label])}</strong><strong class="state-${b.coverage[label]}">${statusLabel(b.coverage[label])}</strong></div>
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
