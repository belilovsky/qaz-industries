const assert = require('node:assert/strict');
const test = require('node:test');

const runtime = require('../runtime.js');

function versionDocument(version) {
  return {
    querySelector(selector) {
      assert.equal(selector, 'meta[name="qaz-asset-version"]');
      return { getAttribute: () => version };
    },
  };
}

test('escapeHtml encodes every HTML-sensitive character', () => {
  assert.equal(runtime.escapeHtml('<a title="x&y\'">'), '&lt;a title=&quot;x&amp;y&#39;&quot;&gt;');
});

test('httpsHref accepts public HTTPS and rejects unsafe external URLs', () => {
  assert.equal(runtime.httpsHref('https://example.org/path?a=1&b=2'), 'https://example.org/path?a=1&amp;b=2');
  assert.throws(() => runtime.httpsHref('http://example.org'), /Unsupported external URL/);
  assert.throws(() => runtime.httpsHref('https://user:secret@example.org'), /Unsupported external URL/);
});

test('assetUrl binds a local path to the release marker', () => {
  assert.equal(runtime.assetUrl('data/snapshot.v1.json', versionDocument('abc/123')), 'data/snapshot.v1.json?v=abc%2F123');
  assert.throws(() => runtime.assetUrl('../private.json'), /Unsupported local asset path/);
  assert.throws(() => runtime.assetUrl('https://example.org/data.json'), /Unsupported local asset path/);
});

test('fetchJsonAsset enforces transport and payload validation', async () => {
  let request;
  const payload = { schema_version: 'example-v1' };
  const result = await runtime.fetchJsonAsset('data/example.json', {
    documentRef: versionDocument('release-1'),
    fetchImpl: async (url, options) => {
      request = { url, options };
      return { ok: true, status: 200, json: async () => payload };
    },
    validate: (value) => value.schema_version === 'example-v1',
  });

  assert.equal(result, payload);
  assert.deepEqual(request, {
    url: 'data/example.json?v=release-1',
    options: { cache: 'no-store', credentials: 'same-origin' },
  });

  await assert.rejects(
    runtime.fetchJsonAsset('data/example.json', {
      fetchImpl: async () => ({ ok: false, status: 503 }),
    }),
    /HTTP 503/,
  );
  await assert.rejects(
    runtime.fetchJsonAsset('data/example.json', {
      fetchImpl: async () => ({ ok: true, status: 200, json: async () => payload }),
      validate: () => false,
    }),
    /failed contract validation/,
  );
});
