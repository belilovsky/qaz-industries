(function (root, factory) {
  'use strict';

  const locale = Object.freeze(factory(root));
  if (typeof module === 'object' && module.exports) module.exports = locale;
  if (root) root.QAZ_LOCALE = locale;
}(typeof globalThis === 'undefined' ? this : globalThis, function (root) {
  'use strict';

  const SUPPORTED_LOCALES = Object.freeze(['ru-RU', 'kk-KZ', 'en-US']);
  const DEFAULT_LOCALE = 'ru-RU';
  const MISSING = '—';
  const messages = Object.freeze({
    loading: 'Загружаем проверенный срез…',
    empty: 'Публичных значений пока нет.',
    error: 'Срез не прошёл проверку. Значения скрыты.',
    offline: 'Источник временно недоступен. Показаны только границы контракта.',
    stale: 'Срез устарел. Дождитесь следующего проверенного выпуска.',
    success: 'Проверенный срез доступен.',
    'contract-only': 'Доступен только контракт; наблюдение ещё не опубликовано.',
  });
  const localeLanguage = Object.freeze({ 'ru-RU': 'ru', 'kk-KZ': 'kk', 'en-US': 'en' });
  const sourceNodes = typeof WeakMap === 'function' ? new WeakMap() : null;
  const sourceAttributes = typeof WeakMap === 'function' ? new WeakMap() : null;
  const listeners = [];
  let activeLocale = DEFAULT_LOCALE;
  let catalog = null;
  let catalogPromise = null;
  let observer = null;
  let applyQueued = false;

  function localeOf(value) {
    return SUPPORTED_LOCALES.includes(value) ? value : DEFAULT_LOCALE;
  }

  function currentLocale() {
    return activeLocale;
  }

  function number(value, options = {}) {
    if (value === null || value === undefined || value === '') return MISSING;
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return MISSING;
    const locale = localeOf(options.locale || activeLocale);
    const maximumFractionDigits = Number.isInteger(options.maximumFractionDigits)
      ? Math.max(0, Math.min(6, options.maximumFractionDigits))
      : 2;
    const minimumFractionDigits = Number.isInteger(options.minimumFractionDigits)
      ? Math.max(0, Math.min(maximumFractionDigits, options.minimumFractionDigits))
      : 0;
    return new Intl.NumberFormat(locale, {
      useGrouping: true,
      maximumFractionDigits,
      minimumFractionDigits,
    }).format(numeric);
  }

  function date(value, options = {}) {
    const parsed = new Date(String(value));
    if (Number.isNaN(parsed.getTime())) return MISSING;
    const locale = localeOf(options.locale || activeLocale);
    const dateStyle = options.dateStyle || 'long';
    return new Intl.DateTimeFormat(locale, {
      dateStyle,
      timeZone: options.timeZone || 'UTC',
    }).format(parsed);
  }

  function unit(value, unitLabel, options = {}) {
    const formatted = number(value, options);
    if (formatted === MISSING) return MISSING;
    return unitLabel ? `${formatted} ${unitLabel}` : formatted;
  }

  function snapshotState(retrievedAt, now = Date.now(), staleAfterDays = 31) {
    if (!retrievedAt) return 'empty';
    const timestamp = Date.parse(String(retrievedAt));
    if (Number.isNaN(timestamp)) return 'error';
    const age = now - timestamp;
    if (age < 0) return 'error';
    return age > staleAfterDays * 24 * 60 * 60 * 1000 ? 'stale' : 'success';
  }

  function message(state) {
    return messages[state] || messages.error;
  }

  function normalized(value) {
    return String(value).replace(/\s+/g, ' ').trim();
  }

  function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function translateString(value, locale = activeLocale) {
    const source = normalized(value);
    if (!source || locale === DEFAULT_LOCALE || !catalog?.translations?.[locale]) return source;
    const dictionary = catalog.translations[locale];
    if (dictionary[source]) return dictionary[source];
    let translated = source;
    const keys = Object.keys(dictionary)
      .filter((key) => key.length >= 3 && key !== source && translated.includes(key))
      .sort((a, b) => b.length - a.length);
    keys.forEach((key) => {
      translated = translated.replace(new RegExp(escapeRegExp(key), 'g'), dictionary[key]);
    });
    return translated;
  }

  function t(value, options = {}) {
    return translateString(value, localeOf(options.locale || activeLocale));
  }

  function preserveWhitespace(original, replacement) {
    const leading = String(original).match(/^\s*/)?.[0] || '';
    const trailing = String(original).match(/\s*$/)?.[0] || '';
    return `${leading}${replacement}${trailing}`;
  }

  function translateTextNode(node) {
    if (!sourceNodes) return;
    if (!sourceNodes.has(node)) sourceNodes.set(node, node.nodeValue || '');
    const original = sourceNodes.get(node) || '';
    node.nodeValue = preserveWhitespace(original, translateString(original));
  }

  function translateAttribute(element, attribute) {
    if (!sourceAttributes) return;
    if (!sourceAttributes.has(element)) sourceAttributes.set(element, {});
    const values = sourceAttributes.get(element);
    if (!values.__translated) values.__translated = Object.create(null);
    const current = element.getAttribute(attribute) || '';
    if (!(attribute in values)) {
      values[attribute] = current;
    } else if (current !== values[attribute] && current !== values.__translated[attribute]) {
      // Runtime code may intentionally replace an attribute (for example a
      // theme toggle's current name). Treat that value as the new source so
      // the next catalog pass cannot restore an earlier state.
      values[attribute] = current;
    }
    const original = values[attribute];
    if (original) {
      const translated = translateString(original);
      element.setAttribute(attribute, translated);
      values.__translated[attribute] = translated;
    }
  }

  function applyDocument(documentRef) {
    if (!documentRef || !catalog) return;
    const rootElement = documentRef.documentElement;
    if (rootElement) {
      rootElement.lang = localeLanguage[activeLocale];
      rootElement.dataset.avLocale = activeLocale;
      rootElement.dataset.avLocaleState = 'ready';
    }
    documentRef.querySelectorAll('[data-locale-select]').forEach((select) => {
      select.value = activeLocale;
      select.setAttribute('aria-label', t('Язык интерфейса'));
    });
    const walker = documentRef.createTreeWalker(documentRef, 4);
    let node;
    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (parent && (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE')) continue;
      translateTextNode(node);
    }
    documentRef.querySelectorAll('[aria-label], [title], [alt], [placeholder], meta[content]').forEach((element) => {
      ['aria-label', 'title', 'alt', 'placeholder', 'content'].forEach((attribute) => {
        if (element.hasAttribute(attribute)) translateAttribute(element, attribute);
      });
    });
  }

  function queueApply(documentRef) {
    if (applyQueued) return;
    applyQueued = true;
    Promise.resolve().then(() => {
      applyQueued = false;
      applyDocument(documentRef);
    });
  }

  function observeDocument(documentRef) {
    if (observer || typeof MutationObserver !== 'function' || !documentRef?.body) return;
    observer = new MutationObserver(() => queueApply(documentRef));
    observer.observe(documentRef.body, { childList: true, subtree: true });
  }

  async function loadCatalog(documentRef) {
    if (catalog) return catalog;
    if (catalogPromise) return catalogPromise;
    const fetchImpl = root?.fetch || (typeof fetch === 'function' ? fetch : null);
    if (typeof fetchImpl !== 'function') return null;
    catalogPromise = fetchImpl('data/ui-locale.v1.json', { cache: 'no-store', credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw new Error(`UI locale HTTP ${response.status}`);
        return response.json();
      })
      .then((payload) => {
        if (payload?.schema_version !== 'qaz-industries-ui-locale-v1') throw new Error('Invalid UI locale contract');
        if (!payload?.translations?.['kk-KZ'] || !payload?.translations?.['en-US']) throw new Error('Incomplete UI locale matrix');
        catalog = payload;
        applyDocument(documentRef);
        observeDocument(documentRef);
        return catalog;
      })
      .catch((error) => {
        catalogPromise = null;
        if (documentRef?.documentElement) documentRef.documentElement.dataset.avLocaleState = 'degraded';
        if (root?.console?.warn) root.console.warn('QAZ locale catalog unavailable:', error);
        return null;
      });
    return catalogPromise;
  }

  function setLocale(value, persist = true) {
    const nextLocale = localeOf(value);
    activeLocale = nextLocale;
    const documentRef = root?.document || (typeof document === 'undefined' ? null : document);
    if (persist) {
      try { root?.localStorage?.setItem('qaz-industries-locale', nextLocale); } catch (_) {}
    }
    documentRef?.querySelectorAll('[data-locale-select]').forEach((select) => { select.value = nextLocale; });
    if (documentRef?.documentElement) {
      documentRef.documentElement.lang = localeLanguage[nextLocale];
      documentRef.documentElement.dataset.avLocale = nextLocale;
    }
    listeners.slice().forEach((listener) => listener(nextLocale));
    void loadCatalog(documentRef).then(() => applyDocument(documentRef));
    return nextLocale;
  }

  function onChange(listener) {
    if (typeof listener !== 'function') return () => {};
    listeners.push(listener);
    return () => {
      const index = listeners.indexOf(listener);
      if (index >= 0) listeners.splice(index, 1);
    };
  }

  function bindDocument(documentRef) {
    documentRef?.querySelectorAll('[data-locale-select]').forEach((select) => {
      if (select.dataset.avLocaleBound === 'true') return;
      select.dataset.avLocaleBound = 'true';
      select.value = activeLocale;
      select.addEventListener('change', () => setLocale(select.value));
    });
  }

  function boot() {
    const documentRef = root?.document || (typeof document === 'undefined' ? null : document);
    if (!documentRef) return;
    bindDocument(documentRef);
    void loadCatalog(documentRef);
  }

  try {
    const stored = root?.localStorage?.getItem('qaz-industries-locale');
    activeLocale = localeOf(stored);
  } catch (_) {}
  if (root?.document) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', boot, { once: true });
    else boot();
  }

  return {
    DEFAULT_LOCALE,
    MISSING,
    SUPPORTED_LOCALES,
    currentLocale,
    date,
    loadCatalog,
    localeOf,
    message,
    number,
    onChange,
    setLocale,
    snapshotState,
    t,
    translateString,
    unit,
  };
}));
