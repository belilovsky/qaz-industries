const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const root = path.resolve(__dirname, '..');

test('public machine discovery is generated from the safe route allowlist', () => {
  execFileSync('python3', ['scripts/build_discovery.py', '--check'], { cwd: root, stdio: 'pipe' });
  const source = JSON.parse(fs.readFileSync(path.join(root, 'data/public-discovery.v1.json'), 'utf8'));
  const index = JSON.parse(fs.readFileSync(path.join(root, 'ai-index.json'), 'utf8'));
  const llms = fs.readFileSync(path.join(root, 'llms.txt'), 'utf8');

  assert.equal(index.schema_version, 'qaz-industries-ai-index-v1');
  assert.equal(index.product_id, 'qaz-industries');
  assert.equal(index.canonical_url, 'https://qaz.industries');
  assert.equal(index.public_safe, true);
  assert.deepEqual(index.boundaries, {
    direct_browser_upstream_access: false,
    external_runtime_data_calls: false,
    credentials_and_private_data: 'excluded',
  });
  assert.deepEqual(index.entrypoints.map(({ id, kind, title_ru }) => ({ id, kind, title_ru })), source.entrypoints.map(({ id, kind, title_ru }) => ({ id, kind, title_ru })));
  for (const entry of index.entrypoints) {
    assert.match(entry.url, /^https:\/\/qaz\.industries\//);
    assert.ok(llms.includes(entry.url), `llms.txt must include ${entry.id}`);
  }
  assert.match(llms, /Generated from: data\/public-discovery\.v1\.json/);
  assert.doesNotMatch(llms, /qz\.energy|qazaqstan\.space|token|password/i);
});
