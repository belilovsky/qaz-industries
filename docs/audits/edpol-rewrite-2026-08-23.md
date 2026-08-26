# EdPol rewrite record — 2026-08-23

Policy evidence was read from `https://edpol.pro/rules/editorial-language-policy.json`:
`edpol-editorial-language-policy-v1@1.1.0`, SHA-256
`3d2c66102da7f3066b6609581067a838035d7813a73366587a1437f55d2bdb76`.

The final visible route and runtime-copy scan covered `index.html`,
`industry.html`, `benchmarks.html`, `publication.html`, `app.js`,
`site-shell.js`, `profile-view.js`, `qazgeo-map.js` and `industry.js`:
9/9 files scanned, no skipped source.

- Rewrote the hero's generic claim into the concrete page title **«Профили
  отраслей»**. Its map, source and release actions remain adjacent.
- Replaced decorative eyebrow treatment with neutral semantic section context;
  no copy was silently removed from RU/KK/EN coverage.
- Repaired the runtime AVDS badge label: the dynamic 92 value now uses
  **«92 процента»**, and the same source label is translated through the local
  KK/EN catalog after a locale change.
- The final deterministic scan has one `structural-candidate`: the internal
  QazGeo enum `coverage.status === 'unknown'`. It is a machine-status test,
  not visible editorial prose; changing it would alter an upstream contract.
  The visible fallback remains **«объём не наблюдался»**.
- The EdPol publication ledger is still `review-required`. No source, rights
  or legal review is claimed complete, no content body is sent externally and
  no EdPol production write occurred.

Closure: the deterministic policy-only scan has no `policy-exact` finding;
the local catalog, terminology gate and full product check must pass after the
rewrite. The remaining enum candidate is documented rather than misclassified
as editorial text.
