(function (root, factory) {
  'use strict';

  const runtime = Object.freeze(factory());
  if (typeof module === 'object' && module.exports) module.exports = runtime;
  if (root) root.QAZ_RUNTIME = runtime;
}(typeof globalThis === 'undefined' ? this : globalThis, function () {
  'use strict';

  const htmlEntities = Object.freeze({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  });
  const localAssetPattern = /^[A-Za-z0-9][A-Za-z0-9._/-]*$/;

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (character) => htmlEntities[character]);
  }

  function httpsHref(value) {
    const url = new URL(String(value));
    if (url.protocol !== 'https:' || url.username || url.password) {
      throw new Error(`Unsupported external URL: ${value}`);
    }
    return escapeHtml(url.href);
  }

  function assetVersion(documentRef) {
    const documentObject = documentRef || (typeof document === 'undefined' ? null : document);
    const marker = documentObject?.querySelector('meta[name="qaz-asset-version"]');
    return marker?.getAttribute('content') || 'source';
  }

  function assetUrl(path, documentRef) {
    const localPath = String(path);
    if (!localAssetPattern.test(localPath) || localPath.startsWith('/') || localPath.includes('..')) {
      throw new Error(`Unsupported local asset path: ${path}`);
    }
    return `${localPath}?v=${encodeURIComponent(assetVersion(documentRef))}`;
  }

  async function fetchJsonAsset(path, options = {}) {
    const fetchImpl = options.fetchImpl || (typeof fetch === 'undefined' ? null : fetch);
    if (typeof fetchImpl !== 'function') throw new Error('Fetch API is unavailable');

    const response = await fetchImpl(assetUrl(path, options.documentRef), {
      cache: 'no-store',
      credentials: 'same-origin',
    });
    if (!response?.ok) throw new Error(`${path} HTTP ${response?.status ?? 'unknown'}`);

    const payload = await response.json();
    if (options.validate && options.validate(payload) === false) {
      throw new Error(`${path} failed contract validation`);
    }
    return payload;
  }

  return {
    assetUrl,
    assetVersion,
    escapeHtml,
    fetchJsonAsset,
    httpsHref,
  };
}));
