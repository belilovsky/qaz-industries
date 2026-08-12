(function (root, factory) {
  'use strict';

  const locale = Object.freeze(factory());
  if (typeof module === 'object' && module.exports) module.exports = locale;
  if (root) root.QAZ_LOCALE = locale;
}(typeof globalThis === 'undefined' ? this : globalThis, function () {
  'use strict';

  const SUPPORTED_LOCALES = Object.freeze(['ru-RU', 'kk-KZ', 'en-US']);
  const DEFAULT_LOCALE = 'ru-RU';
  const MISSING = '—';

  function localeOf(value) {
    return SUPPORTED_LOCALES.includes(value) ? value : DEFAULT_LOCALE;
  }

  function number(value, options = {}) {
    if (value === null || value === undefined || value === '') return MISSING;
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return MISSING;
    const locale = localeOf(options.locale);
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
    const locale = localeOf(options.locale);
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
    const messages = {
      loading: 'Загружаем проверенный срез…',
      empty: 'Публичных значений пока нет.',
      error: 'Срез не прошёл проверку. Значения скрыты.',
      offline: 'Источник временно недоступен. Показаны только границы контракта.',
      stale: 'Срез устарел. Дождитесь следующего проверенного выпуска.',
      success: 'Проверенный срез доступен.',
      'contract-only': 'Доступен только контракт; наблюдение ещё не опубликовано.',
    };
    return messages[state] || messages.error;
  }

  return {
    DEFAULT_LOCALE,
    MISSING,
    SUPPORTED_LOCALES,
    date,
    localeOf,
    message,
    number,
    snapshotState,
    unit,
  };
}));
