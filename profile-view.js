(function (root, factory) {
  'use strict';

  const profileView = Object.freeze(factory());
  if (typeof module === 'object' && module.exports) module.exports = profileView;
  if (root) root.QAZ_PROFILE_VIEW = profileView;
}(typeof globalThis === 'undefined' ? this : globalThis, function () {
  'use strict';

  const coverageStates = new Set(['ready', 'partial', 'gap']);
  const fallbackLocale = {
    number(value, options = {}) {
      const numeric = Number(value);
      return Number.isFinite(numeric) ? new Intl.NumberFormat('ru-RU', { maximumFractionDigits: options.maximumFractionDigits ?? 2 }).format(numeric) : '—';
    },
    date(value) {
      const parsed = new Date(String(value));
      return Number.isNaN(parsed.getTime()) ? '—' : new Intl.DateTimeFormat('ru-RU', { dateStyle: 'long', timeZone: 'UTC' }).format(parsed);
    },
    message(state) {
      return ({
        loading: 'Загружаем проверенный срез…',
        empty: 'Публичных значений пока нет.',
        offline: 'Источник временно недоступен. Показаны только границы контракта.',
        stale: 'Срез устарел. Дождитесь следующего проверенного выпуска.',
        error: 'Срез не прошёл проверку. Значения скрыты.',
      })[state] || 'Состояние среза не определено.';
    },
    snapshotState(value) {
      if (!value) return 'empty';
      const timestamp = Date.parse(String(value));
      if (Number.isNaN(timestamp) || timestamp > Date.now()) return 'error';
      return Date.now() - timestamp > 31 * 24 * 60 * 60 * 1000 ? 'stale' : 'success';
    },
    unit(value, unitLabel, options = {}) {
      const formatted = this.number(value, options);
      return formatted === '—' ? formatted : `${formatted} ${unitLabel || ''}`.trim();
    },
  };

  function localeContract() {
    return (typeof globalThis !== 'undefined' && globalThis.QAZ_LOCALE) || fallbackLocale;
  }

  function setState(element, state) {
    if (!element) return;
    element.dataset.avState = state;
    element.classList.toggle('av-state--loading', state === 'loading');
    element.classList.toggle('av-state--success', state === 'success');
    element.classList.toggle('av-state--error', state === 'error');
    element.classList.toggle('av-state--offline', state === 'offline');
    element.classList.toggle('av-state--stale', state === 'stale');
    element.classList.toggle('av-state--empty', state === 'empty');
    element.classList.toggle('av-state--contract-only', state === 'contract-only');
  }

  function stateCard(title, body, state) {
    const safeState = ['loading', 'empty', 'offline', 'stale', 'error'].includes(state) ? state : 'empty';
    const loadingClass = safeState === 'loading' ? ' av-skeleton' : '';
    return `<div class="av-empty-state av-state--${safeState}${loadingClass}" data-av-state="${safeState}"><strong class="av-empty-state__title">${title}</strong><p class="av-empty-state__body">${body}</p></div>`;
  }

  function coverageState(value) {
    if (!coverageStates.has(value)) throw new Error(`Unsupported coverage state: ${value}`);
    return value;
  }

  function statusLabel(status) {
    return status === 'ready' ? 'Готово' : status === 'partial' ? 'Частично' : 'Пробел';
  }

  function dateLabel(value) {
    const locale = localeContract();
    return locale.date(`${value}T00:00:00Z`) === '—' ? value : locale.date(`${value}T00:00:00Z`);
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
    const locale = localeContract();
    if (Number.isFinite(coverage.geographies)) parts.push(`${locale.number(coverage.geographies)} географий`);
    if (Number.isFinite(coverage.segments)) parts.push(`${locale.number(coverage.segments)} сегментов`);
    if (Number.isFinite(coverage.features)) parts.push(`${locale.number(coverage.features)} объектов`);
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

    function renderTerritory(snapshot, options = {}) {
      const status = required('#territory-status');
      const grid = required('#territory-grid');
      if (!snapshot) {
        const state = options.loading ? 'loading' : (options.state || 'offline');
        setState(status, state);
        status.textContent = localeContract().message(state);
        grid.innerHTML = stateCard('Территориальный срез', state === 'loading' ? 'Проверяем локальный выпуск QazGeo…' : 'География профиля остаётся обзорной и не получает непроверенные значения.', state);
        return;
      }
      const state = localeContract().snapshotState(snapshot.retrieved_at);
      setState(status, state);
      const provider = snapshot.provider;
      status.textContent = `${state === 'stale' ? localeContract().message('stale') + ' · ' : ''}Проверенный статический срез · ${provider.service} · ревизия ${provider.source_revision} · получен ${dateLabel(snapshot.retrieved_at.slice(0, 10))}`;
      const cards = [
        ['Регионов', snapshot.coverage.regions, 'национальная территориальная основа'],
        ['Городов', snapshot.coverage.cities, 'публичный географический каталог'],
        ['Точек интереса', snapshot.coverage.pois, 'без передачи точных координат в QAZ'],
      ];
      if (!cards.some(([, value]) => Number.isFinite(value))) {
        setState(status, 'empty');
        grid.innerHTML = stateCard('Территориальный срез пуст', localeContract().message('empty'), 'empty');
        return;
      }
      grid.innerHTML = cards.map(([label, value, note]) => `
        <article class="av-card av-card--outlined"><span>${escapeHtml(label)}</span><strong>${escapeHtml(localeContract().number(value))}</strong><p>${escapeHtml(note)}</p></article>
      `).join('');
    }

    function renderPulse(snapshot, territorySnapshot, options = {}) {
      const status = required('#pulse-status');
      const grid = required('#pulse-grid');
      const boundary = required('#pulse-boundary-state');
      if (!snapshot) {
        const state = options.loading ? 'loading' : (options.state || 'offline');
        setState(status, state);
        status.textContent = localeContract().message(state);
        grid.innerHTML = stateCard('Макро-срез QazLake', state === 'loading' ? 'Проверяем локальный выпуск…' : 'Отраслевой профиль продолжает работать без него.', state);
      } else {
        const provider = snapshot.provider;
        const state = localeContract().snapshotState(snapshot.retrieved_at);
        setState(status, state);
        status.innerHTML = `${state === 'stale' ? escapeHtml(localeContract().message('stale')) + ' · ' : ''}Проверенный статический срез · ${escapeHtml(provider.service)} · ревизия ${escapeHtml(provider.source_revision)} · получен ${escapeHtml(dateLabel(snapshot.retrieved_at.slice(0, 10)))}`;
        if (!Array.isArray(snapshot.indicators) || snapshot.indicators.length === 0) {
          setState(status, 'empty');
          grid.innerHTML = stateCard('Макро-срез пуст', localeContract().message('empty'), 'empty');
        } else {
          grid.innerHTML = snapshot.indicators.map((item) => `
          <article class="av-card av-card--outlined">
            <span>${escapeHtml(item.label)}</span>
            <strong>${escapeHtml(localeContract().unit(item.value, item.unit, { maximumFractionDigits: 2 }))}</strong>
            <p>на ${escapeHtml(dateLabel(item.as_of))} · <a href="${httpsHref(item.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(item.source)} ↗</a></p>
          </article>
          `).join('');
        }
      }
      renderTerritory(territorySnapshot, {
        loading: options.territoryLoading ?? options.loading,
        state: options.territoryState ?? options.state,
      });
      const unavailable = [
        ...(snapshot?.unavailable_modules || []),
        ...(territorySnapshot?.unavailable_modules || []),
      ].map((item) => item.reason).join(' ');
      boundary.textContent = unavailable || 'Публичные контракты QazLake и QazGeo проверены отдельно перед включением.';
    }

    function renderLayerRegistry(registry, options = {}) {
      const status = required('#layer-registry-status');
      const grid = required('#layer-registry-grid');
      if (!registry) {
        const state = options.loading ? 'loading' : (options.state || 'offline');
        setState(status, state);
        status.textContent = localeContract().message(state);
        grid.innerHTML = stateCard('Реестр слоёв QazGeo', state === 'loading' ? 'Проверяем локальный выпуск реестра…' : 'Значения не подставляются без проверенного среза.', state);
        return;
      }
      const state = localeContract().snapshotState(registry.retrieved_at);
      setState(status, state);
      const provider = registry.provider;
      const contractOnlyCount = registry.layers.filter((layer) => layer.dataset_status === 'contract_only').length;
      status.textContent = `${state === 'stale' ? localeContract().message('stale') + ' · ' : ''}Проверенный реестр слоёв · ${provider.service} · ревизия ${provider.source_revision} · ${localeContract().number(registry.layers.length)} контрактов; ${localeContract().number(contractOnlyCount)} пока описывают только план подключения.`;
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
              <span class="av-badge ${badgeClass}" data-av-state="${layer.dataset_status === 'contract_only' ? 'contract-only' : 'success'}">${escapeHtml(layerStatusLabel(layer))}</span>
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
      const periodComparison = documentRef.querySelector('#period-comparison');
      if (periodComparison) {
        const comparisons = profile.indicators.filter((item) => /\sк\s|к предыдущему году|сравнени/i.test(item.period || '') || /сопоставлен/i.test(item.note || ''));
        periodComparison.innerHTML = comparisons.length
          ? comparisons.map((item) => `<div class="av-period-comparison__row" role="listitem"><span class="av-period-comparison__label">${escapeHtml(item.name)}</span><strong>${escapeHtml(localeContract().unit(item.value, item.unit, { maximumFractionDigits: 2 }))}</strong><span>${escapeHtml(item.period)}</span><a href="${httpsHref(item.url)}" target="_blank" rel="noreferrer">Источник ↗</a></div>`).join('')
          : stateCard('Сопоставление периодов', 'В текущем выпуске нет подтверждённых пар периодов.', 'empty');
        periodComparison.dataset.avState = comparisons.length ? 'success' : 'empty';
      }
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
      const chart = documentRef.querySelector('#coverage-chart');
      if (chart) {
        const weight = { gap: 0, partial: 0.5, ready: 1 };
        const stateText = { gap: 'Пробел', partial: 'Частично', ready: 'Готово' };
        const profileRows = [profileA, profileB].map((profile) => `
          <div class="av-coverage-chart__group" data-profile="${escapeHtml(profile.id)}">
            <h4 class="av-coverage-chart__label">${escapeHtml(profile.short)}</h4>
            <div class="av-coverage-chart__plot" role="list" aria-label="Покрытие ${escapeHtml(profile.name)}">
              ${rows.map((label) => {
                const state = coverageState(profile.coverage[label]);
                return `<div class="av-coverage-chart__row" role="listitem"><span class="av-coverage-chart__label">${escapeHtml(label)}</span><span class="av-coverage-chart__track" role="img" aria-label="${escapeHtml(stateText[state])}"><span class="av-coverage-chart__bar av-coverage-chart__bar--${state}" style="--coverage-value:${weight[state]}"></span></span><span class="av-coverage-chart__value">${escapeHtml(stateText[state])}</span></div>`;
              }).join('')}
            </div>
          </div>
        `).join('');
        chart.innerHTML = `<div class="av-coverage-chart__header"><h3 class="av-coverage-chart__title">Статусная диаграмма покрытия</h3><p class="av-coverage-chart__source">Источник: data/industry-profiles.v1.json · таблица ниже — альтернативный вид</p></div><ul class="av-coverage-chart__legend" aria-label="Легенда состояний"><li><span class="av-coverage-chart__swatch av-coverage-chart__swatch--ready" aria-hidden="true"></span>Готово</li><li><span class="av-coverage-chart__swatch av-coverage-chart__swatch--partial" aria-hidden="true"></span>Частично</li><li><span class="av-coverage-chart__swatch av-coverage-chart__swatch--gap" aria-hidden="true"></span>Пробел</li></ul>${profileRows}`;
      }
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
    stateCard,
  };
}));
