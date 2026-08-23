# Platform integration audit — QAZ.INDUSTRIES — 2026-08-23

## Scope and identity

- Canonical source: `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries`
  on `main` at `c85f78c5e3f853b779b2e817f33263a765466407` plus the uncommitted
  local candidate described in this repository.
- Runtime/public entrypoint: `https://qaz.industries/`.
- Audit cut-off: `2026-08-23T13:26:25Z`.
- Evidence boundaries: the Platform schema and catalog redirect the public
  probe to authentication HTML; the bounded local source does not contain the
  public AVDS 4.7.0 source revision. No external checkout, registry or runtime
  was changed.

## Verdict

`blocked`

- Applicable rows: `9`.
- Covered: `5`; documented: `2`; stale: `0`; missing: `1`; conflicting: `0`;
  unverifiable: `1`.
- Coverage: `5/9 = 56%`.

This is a strict Platform-acceptance result, not the AVDS product-quality
metric. It cannot be stronger while the root `qdev-project.json` lacks a
published or authenticated schema and the AVDS control-plane registration has
no inspectable source receipt.

## Coverage matrix

| Area | Requirement | Expected relation | Evidence inspected | State | Observed at | Finding / next action |
|---|---|---|---|---|---|---|
| Identity | required | manifest ↔ catalog ↔ source ↔ runtime use one project ID | source identity, public health, absent `qdev-project.json` | missing | 2026-08-23 | Do not invent a manifest; Platform owner must supply active schema or accepted receipt. |
| QazStack | required | consumer contract names mode, assets and verification | `qazstack-consumer.json`, `qazstack-thematic-product.json`, local contract gate | documented | 2026-08-23 | Project-side contract is coherent; external registry comparison remains outside scope. |
| AV DS | required | declared adapter/version is used by shipped interface | vendored 4.6.0 receipt, tokens, component/route/a11y gates; public AVDS release observation | unverifiable | 2026-08-23 | Local artifact is verified; external control-plane registration and 4.7.0 source are not inspectable. No upgrade was performed. |
| QazPipe | optional | input/processing boundary is explicit | static-product architecture and consumer boundary | not_applicable | 2026-08-23 | Owner: QAZ frontend owner; no QazPipe input or processing is declared. Review by 2026-11-23 if an ingestion feature is introduced. |
| QazLake | required | reviewed public projection, freshness and degraded state are explicit | public snapshot, source registry, state contracts and local checks | covered | 2026-08-23 | Three reviewed macro indicators only; regional/water modules remain visibly degraded. |
| QazCompute | optional | permitted compute interface is explicit | static-product architecture and no compute adapter | not_applicable | 2026-08-23 | Owner: QAZ frontend owner; no remote compute is declared. Review by 2026-11-23 if server-side computation is introduced. |
| QazGeo | required | geographic dataset contract and fallback are explicit | sanitized GeoJSON, layer registry, map fallback and local checks | covered | 2026-08-23 | Twenty regional geometries are public-safe; sensitive coordinates are excluded. |
| Identity/security | required | access boundary and mutation controls match behavior | static architecture, CSP/security and contract gates | covered | 2026-08-23 | Public surface has no authenticated mutation path or direct upstream credentials. |
| Data/privacy | required | public/private fields and provenance remain separated | QazStack consumer, source registry, publication policy and tests | covered | 2026-08-23 | Browser uses same-origin reviewed projections only; raw/private material is excluded. |
| Routes/UI | required | navigation, states and responsive behavior are proven | route ledger, accessibility, locale, responsive and visual gates | covered | 2026-08-23 | All four routes have local proof; AVDS consumer-registration gate remains intentionally false. |
| Delivery/operations | required | CI, health, release identity, rollback evidence are coherent | historical release receipt, current public health and local gates | documented | 2026-08-23 | Public runtime remains `20260815T124544Z-c85f78c5e3f8`; this candidate has not been deployed. |

## Cross-system consistency

| Claim / edge | Project evidence | Platform evidence | Result |
|---|---|---|---|
| QAZ.INDUSTRIES → QazStack | thematic and consumer contracts with same-origin reviewed assets | no registry comparison in this scope | documented |
| QAZ.INDUSTRIES → QazLake | reviewed snapshot, provenance and degraded states | no raw browser/API access by design | covered |
| QAZ.INDUSTRIES → QazGeo | sanitized region asset and layer contracts | no direct browser API by design | covered |
| QAZ.INDUSTRIES → AVDS | pinned `@sgeo/ui-kit@4.6.0` tarball and digest receipt | public AVDS reports 4.7.0; source SHA is not in bounded source | unverifiable |
| QAZ.INDUSTRIES → Platform catalog/runtime route | `data/platform-registration-request.v1.json` | health is reachable; schema and catalog return authentication HTML | missing |

## Gates run

| Gate | Result | Evidence / limitation |
|---|---|---|
| Manifest/schema | blocked | Root manifest is absent; schema endpoint is auth-gated HTML, not JSON Schema. |
| QazStack integration | passed locally | `python3 scripts/check_public_contracts.py`; no external registry mutation or comparison. |
| Product quality | passed locally | `bash scripts/check.sh` after the closure changes. |
| Product tests/build/security | passed locally | Python and Node checks executed through `scripts/check.sh`. |
| Runtime/public proof | observed | `https://qaz.industries/api/health` serves the pre-candidate release; no deployment was authorised. |

## Remediation queue

| Priority | Owner role | Finding | Concrete next action | Closure proof |
|---|---|---|---|---|
| P1 | AV Platform catalog owner | `qdev-project.json` is missing and the active schema/catalog are not publicly inspectable. | Provide authenticated schema access or an accepted manifest receipt; then create and validate the exact project manifest in this checkout. | Platform-owned record resolves `product_id: qaz-industries`, canonical URL and repository, and validates against the active schema. |
| P1 | AVDS control-plane owner | The local 4.6.0 artifact is verified, but consumer registration and the public 4.7.0 source cannot be proven. | Provide an authenticated consumer registration record and a reviewed 4.7.0 tarball/source receipt. | Exact source revision, artifact digest and consumer ID `qaz_industries` are independently queryable; package upgrade passes all local gates. |

## Boundary notes

The candidate is a static public site. QazPipe, QazCompute and authenticated
identity are not present and therefore do not have hidden fallbacks. Link
metadata is not treated as a data integration. QazLake/QazGeo source data,
credentials and protected Platform pages were not copied, mutated or exposed.
