#!/usr/bin/env node
/** Validate the trusted static data layer before it is rendered into HTML. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = fs.readFileSync(path.join(ROOT, 'industry-data.js'), 'utf8');
const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(source, sandbox, { filename: 'industry-data.js', timeout: 1000 });
const profiles = sandbox.window.QAZ_INDUSTRIES;
const profileRegistry = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'industry-profiles.v1.json'), 'utf8'));
const coverageStates = new Set(['ready', 'partial', 'gap']);

function fail(message) {
  throw new Error(`data contract: ${message}`);
}

function requiredString(value, label) {
  if (typeof value !== 'string' || value.trim() === '') fail(`${label} must be a non-empty string`);
}

function httpsUrl(value, label) {
  requiredString(value, label);
  let url;
  try {
    url = new URL(value);
  } catch {
    fail(`${label} must be an absolute URL`);
  }
  if (url.protocol !== 'https:') fail(`${label} must use HTTPS`);
}

function stringArray(value, label) {
  if (!Array.isArray(value) || value.length === 0) fail(`${label} must be a non-empty array`);
  value.forEach((item, index) => requiredString(item, `${label}[${index}]`));
}

function objectArray(value, label, fields) {
  if (!Array.isArray(value) || value.length === 0) fail(`${label} must be a non-empty array`);
  value.forEach((item, index) => {
    if (!item || typeof item !== 'object') fail(`${label}[${index}] must be an object`);
    fields.forEach((field) => requiredString(item[field], `${label}[${index}].${field}`));
  });
}

if (!profiles || typeof profiles !== 'object' || Array.isArray(profiles)) fail('profiles must be an object');
const entries = Object.entries(profiles);
if (entries.length < 1) fail('at least one profile is required');
const registryEntries = new Map(profileRegistry.profiles.map((profile) => [profile.id, profile]));
if (registryEntries.size !== entries.length) fail('profile registry differs from JavaScript profile count');

for (const [key, profile] of entries) {
  if (!/^[a-z0-9-]+$/.test(key)) fail(`${key}: profile key is invalid`);
  if (!profile || typeof profile !== 'object') fail(`${key}: profile must be an object`);
  for (const field of ['id', 'name', 'short', 'code', 'sourceName', 'sourceReleaseId', 'release', 'status', 'summary', 'about']) {
    requiredString(profile[field], `${key}.${field}`);
  }
  if (profile.id !== key) fail(`${key}.id must equal its profile key`);
  const registryProfile = registryEntries.get(key);
  if (!registryProfile) fail(`${key}: missing from JSON profile registry`);
  if (registryProfile.name !== profile.name) fail(`${key}: JSON/JavaScript name mismatch`);
  if (registryProfile.source !== profile.sourceUrl) fail(`${key}: JSON/JavaScript source mismatch`);
  if (registryProfile.source_release_id !== profile.sourceReleaseId) fail(`${key}: JSON/JavaScript source release mismatch`);
  if (registryProfile.release !== profile.release) fail(`${key}: JSON/JavaScript release mismatch`);
  httpsUrl(profile.sourceUrl, `${key}.sourceUrl`);
  objectArray(profile.kpis, `${key}.kpis`, ['value', 'label', 'period']);
  objectArray(profile.indicators, `${key}.indicators`, ['name', 'value', 'unit', 'period', 'note', 'url']);
  profile.indicators.forEach((item, index) => httpsUrl(item.url, `${key}.indicators[${index}].url`));
  objectArray(profile.chain, `${key}.chain`, ['title', 'text']);
  objectArray(profile.geography, `${key}.geography`, ['title', 'text']);
  stringArray(profile.gaps, `${key}.gaps`);
  if (!profile.coverage || typeof profile.coverage !== 'object' || Array.isArray(profile.coverage)) {
    fail(`${key}.coverage must be an object`);
  }
  const coverage = Object.entries(profile.coverage);
  if (coverage.length < 1) fail(`${key}.coverage must not be empty`);
  coverage.forEach(([label, state]) => {
    requiredString(label, `${key}.coverage label`);
    if (!coverageStates.has(state)) fail(`${key}.coverage.${label} has invalid state`);
  });
  objectArray(profile.sources, `${key}.sources`, ['label', 'url']);
  profile.sources.forEach((item, index) => httpsUrl(item.url, `${key}.sources[${index}].url`));
}

console.log(`data contract: OK (${entries.length} profiles)`);
