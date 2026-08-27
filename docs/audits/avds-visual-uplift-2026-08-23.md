# AVDS visual uplift — 2026-08-23

Mode: **visual uplift**. The three structural decisions below were released in
`7cb44a040c2de1baef0a604d59b1a4b738a8d4dc` as
`20260823T134657Z-7cb44a040c2d`. The follow-up local candidate only repairs
the accessible, localized AVDS badge label and remains uncommitted.

## Product decisions

1. The home route now starts with the functional profile directory rather than
   the slogan «одна картина»; the QazGeo map, source link and release facts
   remain part of the first reading region.
2. Decorative grids, glows, gradients and translucent glass were removed from
   the shell, hero, map, profile, research and publication surfaces. AVDS
   token colour, borders and typographic hierarchy now carry the structure.
3. Decorative eyebrow styling became semantic section context. It identifies
   an information scope but has no ornamental line, glow, badge or counter
   role.
4. The coverage badge keeps its machine-readable evidence but now uses the
   correct Russian percentage form and refreshes its accessible label after a
   locale switch; the compact footer does not gain another decorative element.

## Evidence

- Before evidence: the pre-change local home capture
  `output/playwright/before-home-1280.png`; existing route baselines under
  `tests/visual-baselines/` supplement the historical route reference.
- After evidence: `output/playwright/final/` contains 8 browser captures for
  four public routes at 390 and 1440 CSS pixels.
- [`avds-browser-ledger-2026-08-23.json`](avds-browser-ledger-2026-08-23.json)
  defines the route matrix and portable visual-craft targets.
- [`avds-anti-generative-audit-2026-08-23.json`](avds-anti-generative-audit-2026-08-23.json)
  records seven resolved findings.
- [`avds-visual-craft-audit-2026-08-23.json`](avds-visual-craft-audit-2026-08-23.json)
  covers all eight browser cells: geometry, radii, typography and space.

The portable browser acceptance passed all 8 local-candidate cells. The
anti-generative and visual-craft validators both passed. On 2026-08-23 the
same 8-cell matrix was repeated against `https://qaz.industries/` with matching
`sourceSha` and `runtimeSha` of the published release; it also passed. The two
evidence layers remain distinct: the local candidate includes the uncommitted
localized-badge repair, while live-public proves only the immutable release.

## Version boundary

The product continues to consume the locally hashed and tested
`@sgeo/ui-kit@4.6.0` package. A bounded source inspection did not resolve an
exact public source/release receipt for a newer AVDS line, so no unreviewed
upgrade was performed. If an upgrade is required, the AVDS release maintainer
must provide the exact tarball/source revision and licence receipt; closure is
a pinned artifact, refreshed package/runtime receipt and the same full gate
set. This is an external version-provenance dependency, not evidence that the
current 4.6.0 adapter is broken.
