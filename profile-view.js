(function (root, factory) {
  'use strict';

  const profileView = Object.freeze(factory());
  if (typeof module === 'object' && module.exports) module.exports = profileView;
  if (root) root.QAZ_PROFILE_VIEW = profileView;
}(typeof globalThis === 'undefined' ? this : globalThis, function () {
  'use strict';

  const coverageStates = new Set(['ready', 'partial', 'gap']);

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
      day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
    }).format(date);
  }

  function layerStatusLabel(layer) {
    if (layer.dataset_status === 'contract_only') return 'только контракт';
    if (layer.status === 'stable') return 'стабильный слой';
    return 'проверенная бета';
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
    if (!layer?.freshness?.data_updated_at) return 'Наблюдение не заявлено';
    return `данные на ${dateLabel(layer.freshness.data_updated_at)}`;
  }

  function licenseStatusLabel(status) {
    if (status === 'documented') return 'условия описаны';
    if (status === 'attribution-required') return 'требуется атрибуция';
    return 'проверяется';
  }

  function createProfileView(documentRef, runtime) {
    if (!documentRef || !runtime) throw new Error('Profile view dependencies are required');
    const { escapeHtml, httpsHref } = runtime;

    function required(selector) {
      const element = documentRef.querySelector(selector);
      if (!element) throw new Error(`Profile view element is missing: ${selector}`);
      return element;
    }

    function renderPassport(profile) {
      required('#passport-source').textContent = profile.sourceName;
      required('#passport-release').textContent = profile.release;
      required('#profile-machine-link').setAttribute('aria-label', `Открыть JSON профилей; выбран ${profile.name}`);
    }

    function renderTerritory(snapshot) {
      const status = required('#territory-status');
      const grid = required('#territory-grid');
      if (!snapshot) {
        status.textContent = 'Публичный срез QazGeo недоступен. География профиля остаётся обзорной и не получает непроверенные значения.';
        grid.innerHTML = '';
        return;
      }
      const provider = snapshot.provider;
      status.textContent = `Проверенный статический срез · ${provider.service} · ревизия ${provider.source_revision} · получен ${dateLabel(snapshot.retrieved_at.slice(0, 10))}`;
      const cards = [
        ['Регионов', snapshot.coverage.regions, 'национальная территориальная основа'],
        ['Городов', snapshot.coverage.cities, 'публичный географический каталог'],
        ['Точек интереса', snapshot.coverage.pois, 'без передачи точных координат в QAZ'],
      ];
      grid.innerHTML = cards.map(([label, value, note]) => `
        <article class="av-card av-card--outlined"><span>${escapeHtml(label)}</span><strong>${escapeHtml(Number(value).toLocaleString('ru-RU'))}</strong><p>${escapeHtml(note)}</p></article>
      `).join('');
    }

    function renderPulse(snapshot, territorySnapshot) {
      const status = required('#pulse-status');
      const grid = required('#pulse-grid');
      const boundary = required('#pulse-boundary-state');
      if (!snapshot) {
        status.textContent = 'Публичный срез QazLake недоступен. Отраслевой профиль продолжает работать без него.';
        grid.innerHTML = '';
      } else {
        const provider = snapshot.provider;
        status.innerHTML = `Проверенный статический срез · ${escapeHtml(provider.service)} · ревизия ${escapeHtml(provider.source_revision)} · получен ${escapeHtml(dateLabel(snapshot.retrieved_at.slice(0, 10)))}`;
        grid.innerHTML = snapshot.indicators.map((item) => `
          <article class="av-card av-card--outlined">
            <span>${escapeHtml(item.label)}</span>
            <strong>${escapeHtml(String(item.value).replace('.', ','))}<small>${escapeHtml(item.unit)}</small></strong>
            <p>на ${escapeHtml(dateLabel(item.as_of))} · <a href="${httpsHref(item.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(item.source)} ↗</a></p>
          </article>
        `).join('');
      }
      renderTerritory(territorySnapshot);
      const unavailable = [
        ...(snapshot?.unavailable_modules || []),
        ...(territorySnapshot?.unavailable_modules || []),
      ].map((item) => item.reason).join(' ');
      boundary.textContent = unavailable || 'Публичные контракты QazLake и QazGeo проверены отдельно перед включением.';
    }

    function renderLayerRegistry(registry) {
      const status = required('#layer-registry-status');
      const grid = required('#layer-registry-grid');
      if (!registry) {
        status.textContent = 'Публичный реестр слоёв QazGeo недоступен. Значения не подставляются без проверенного среза.';
        grid.innerHTML = '';
        return;
      }
      const provider = registry.provider;
      const contractOnlyCount = registry.layers.filter((layer) => layer.dataset_status === 'contract_only').length;
      status.textContent = `Проверенный реестр слоёв · ${provider.service} · ревизия ${provider.source_revision} · ${registry.layers.length} контрактов; ${contractOnlyCount} пока описывают только план подключения.`;
      grid.innerHTML = registry.layers.map((layer, index) => {
        const badgeClass = layer.dataset_status === 'contract_only' ? 'av-badge--info' : 'av-badge--success';
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
                <div class="av-layer-registry__metadata-row"><dt>Свежесть</dt><dd>${escapeHtml(layerFreshnessLabel(layer))}</dd></div>
                <div class="av-layer-registry__metadata-row"><dt>Лицензия</dt><dd>${escapeHtml(licenseStatusLabel(layer.license?.status))} · ${escapeHtml(layer.provenance?.attribution || 'QazGeo')}</dd></div>
              </dl>
              <p class="av-layer-registry__limit">${escapeHtml(layer.limitations)}</p>
              <div class="av-layer-registry__actions"><a class="av-layer-registry__action" href="${httpsHref(layer.contract_url)}" target="_blank" rel="noreferrer">Открыть контракт ↗</a><a class="av-layer-registry__source" href="${httpsHref(layer.source_url)}" target="_blank" rel="noreferrer">Источник ↗</a></div>
            </div>
          </article>
        `;
      }).join('');
    }

    function renderProfile(profile) {
      documentRef.title = `${profile.name} — QAZ.INDUSTRIES`;
      required('#toolbar-current').textContent = profile.name;
      required('#profile-code').textContent = profile.code;
      required('#profile-title').textContent = profile.name;
      required('#profile-summary').textContent = profile.summary;
      required('#profile-status').textContent = profile.status;
      required('#profile-release').textContent = profile.release;
      required('#profile-about').textContent = profile.about;
      required('#profile-evidence-source').textContent = profile.sourceName;
      required('#profile-evidence-release').textContent = profile.release;
      const evidenceLink = required('#profile-evidence-link');
      evidenceLink.href = httpsHref(profile.sourceUrl);
      evidenceLink.textContent = `Проверить ${profile.sourceName} ↗`;
      const sourceTop = required('#profile-source-top');
      sourceTop.href = httpsHref(profile.sourceUrl);
      sourceTop.textContent = `${profile.sourceName} ↗`;
      renderPassport(profile);

      documentRef.querySelectorAll('[data-sector]').forEach((button) => {
        const active = button.dataset.sector === profile.id;
        button.setAttribute('aria-pressed', String(active));
        button.classList.toggle('is-active', active);
      });

      required('#profile-kpis').innerHTML = profile.kpis.map((item) => `
        <article class="av-card av-card--outlined"><strong>${escapeHtml(item.value)}</strong><span>${escapeHtml(item.label)}</span><small>${escapeHtml(item.period)}</small></article>
      `).join('');
      required('#indicator-rows').innerHTML = profile.indicators.map((item) => `
        <div class="indicator-row" role="row">
          <strong role="cell">${escapeHtml(item.name)}</strong>
          <span class="indicator-value" role="cell">${escapeHtml(item.value)} <small>${escapeHtml(item.unit)}</small></span>
          <span role="cell">${escapeHtml(item.period)}</span>
          <span role="cell">${escapeHtml(item.note)}</span>
          <a role="cell" href="${httpsHref(item.url)}" target="_blank" rel="noreferrer">открыть ↗</a>
        </div>
      `).join('');
      required('#chain-grid').innerHTML = profile.chain.map((item, index) => `
        <article class="av-card av-card--outlined"><span>0${index + 1}</span><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.text)}</p></article>
      `).join('');
      required('#geography-grid').innerHTML = profile.geography.map((item) => `
        <article class="av-card av-card--outlined"><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.text)}</p></article>
      `).join('');
      required('#coverage-list').innerHTML = Object.entries(profile.coverage).map(([label, status]) => `
        <div><strong>${escapeHtml(label)}</strong><span class="coverage-state state-${coverageState(status)}">${statusLabel(status)}</span></div>
      `).join('');
      required('#gap-list').innerHTML = profile.gaps.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
      required('#source-links').innerHTML = profile.sources.map((item, index) => `
        <article class="av-card av-card--outlined av-source-registry__record">
          <div class="av-card__body av-source-registry__record-body">
            <div class="av-source-registry__title-row">
              <div class="av-source-registry__record-header">
                <p class="av-source-registry__record-eyebrow">0${index + 1} · ПРОВЕРЕННЫЙ ИСТОЧНИК</p>
                <h3>${escapeHtml(item.label)}</h3>
              </div>
              <span class="av-badge av-badge--success">ссылка проверена</span>
            </div>
            <p class="av-source-registry__record-description">Ссылка ведёт к разделу «${escapeHtml(item.label)}». QAZ показывает метаданные ссылки и не копирует исходный реестр.</p>
            <dl class="av-source-registry__metadata">
              <div class="av-source-registry__metadata-row"><dt>Продукт</dt><dd>${escapeHtml(profile.sourceName)}</dd></div>
              <div class="av-source-registry__metadata-row"><dt>Срез</dt><dd>${escapeHtml(profile.release)}</dd></div>
            </dl>
            <div class="av-source-registry__actions"><a class="av-source-registry__action" href="${httpsHref(item.url)}" target="_blank" rel="noreferrer">Открыть источник ↗</a></div>
          </div>
        </article>
      `).join('');
    }

    function renderComparison(profileA, profileB) {
      const rows = Object.keys(profileA.coverage);
      required('#compare-table').innerHTML = `
        <div class="compare-row compare-table-head"><span>Слой профиля</span><strong>${escapeHtml(profileA.short)}</strong><strong>${escapeHtml(profileB.short)}</strong></div>
        ${rows.map((label) => `
          <div class="compare-row"><span>${escapeHtml(label)}</span><strong class="state-${coverageState(profileA.coverage[label])}">${statusLabel(profileA.coverage[label])}</strong><strong class="state-${coverageState(profileB.coverage[label])}">${statusLabel(profileB.coverage[label])}</strong></div>
        `).join('')}
      `;
    }

    return { renderComparison, renderLayerRegistry, renderProfile, renderPulse };
  }

  return {
    coverageState,
    createProfileView,
    dateLabel,
    layerCoverageLabel,
    layerFreshnessLabel,
    layerStatusLabel,
    licenseStatusLabel,
    statusLabel,
  };
}));
