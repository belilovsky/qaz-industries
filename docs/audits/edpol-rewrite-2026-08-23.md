# EdPol rewrite record — 2026-08-23

Policy evidence was read from `https://edpol.pro/rules/editorial-language-policy.json`:
`edpol-editorial-language-policy-v1@1.1.0`, SHA-256
`3d2c66102da7f3066b6609581067a838035d7813a73366587a1437f55d2bdb76`.

The visible route and runtime-copy scan covered `index.html`, `industry.html`,
`benchmarks.html`, `publication.html`, `locale.js`, `industry.js` and
`profile-view.js`.

- Rewrote the hero's generic claim into the concrete page title **«Профили
  отраслей»**. Its map, source and release actions remain adjacent.
- Replaced decorative eyebrow treatment with neutral semantic section context;
  no copy was silently removed from RU/KK/EN coverage.
- The final deterministic scan has one `structural-candidate`: the internal
  QazGeo enum `coverage.status === 'unknown'`. It is a machine-status test,
  not visible editorial prose; changing it would alter an upstream contract.
  The visible fallback remains **«объём не наблюдался»**.
- The EdPol publication ledger is still `review-required`. No source, rights
  or legal review is claimed complete, no content body is sent externally and
  no EdPol production write occurred.

Closure: rewritten user copy is generated into the local catalog, terminology
gate passes, and the remaining enum candidate is documented rather than
misclassified as editorial text.
