# QAZ.INDUSTRIES operations

## Ownership

This repository is the source of truth for the static QAZ.INDUSTRIES surface.
The public runtime is an isolated release tree under the shared public-sites
Caddy instance. Its proxy configuration is shared infrastructure: change only
the QAZ.INDUSTRIES block and its `X-Qaz-Industries-Release` marker, never
replace the whole Caddyfile, mutate generic `X-Qaz-Release` headers, or touch
HAProxy for a content-only release.

## Release procedure

1. Refresh QazLake, QazGeo and the curated layer registry with the three
   `scripts/refresh_*.py` commands. Review every diff; contract-only layers may
   update metadata but must never become fabricated observations.
2. Run `scripts/check.sh`.
3. Commit the reviewed source.
4. Run `scripts/deploy.sh` from a clean worktree.
5. Verify the exact release in `X-Qaz-Industries-Release` and `/api/health`.
6. Verify `index.html`, `industry.html?sector=farm`, `benchmarks.html`,
   `styles.css`, `avds.css`, and both JavaScript files over the public domain.
7. Perform a browser pass at desktop and 390px before accepting the release.

The scheduled `public-contract-monitor.yml` workflow is intentionally
read-only: it probes QazLake/QazGeo and uploads output for review, but never
commits snapshots or deploys them. The detailed junior execution plan is in
[`roadmap-to-ideal.md`](roadmap-to-ideal.md).

The deploy script creates a new immutable release directory and first patches a
candidate Caddyfile with a fail-closed, product-scoped parser. It updates the
bind-mounted file in place, validates Caddy while the old `current` symlink is
still active, then switches the symlink and reloads. A reload failure restores
both the prior Caddyfile and the prior symlink. It retains the active release
plus seven previous releases and the newest eight QAZ-only Caddy backups.

The artifact versions local CSS and JavaScript URLs, so a browser cannot combine
new HTML with stale assets. The deploy fails before switching `current` if the
container's Caddyfile digest differs from the host file, or if its bind mount
does not receive the candidate. After any older operation atomically replaces
the host Caddyfile, restart the named Caddy container once, verify the matching
digests, and retry the QAZ release.

## Boundaries

- Static content only; do not add credentials or private source material.
- The data layer remains local until a public API contract is explicitly owned.
- A local preview or a successful Caddy reload is not public acceptance.
- `unsafe-inline` remains in the CSP until inline bootstrap scripts are moved to
  versioned assets or nonce-based execution. Google Fonts hosts are currently
  allowlisted because the existing stylesheet imports them; self-hosting those
  licensed fonts is tracked in the roadmap.
