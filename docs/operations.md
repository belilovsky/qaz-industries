# QAZ.INDUSTRIES operations

## Ownership

This repository is the source of truth for the static QAZ.INDUSTRIES surface.
The public runtime is an isolated release tree under the shared public-sites
Caddy instance. Its proxy configuration is shared infrastructure: change only
the QAZ.INDUSTRIES block and its `X-Qaz-Industries-Release` marker, never
replace the whole Caddyfile, mutate generic `X-Qaz-Release` headers, or touch
HAProxy for a content-only release.

## Release procedure

1. Run `scripts/check.sh`.
2. Commit the reviewed source.
3. Run `scripts/deploy.sh` from a clean worktree.
4. Verify the exact release in `X-Qaz-Industries-Release` and `/api/health`.
5. Verify `index.html`, `industry.html?sector=farm`, `benchmarks.html`,
   `styles.css`, `avds.css`, and both JavaScript files over the public domain.
6. Perform a browser pass at desktop and 390px before accepting the release.

The deploy script creates a new immutable release directory and first patches a
candidate Caddyfile with a fail-closed, product-scoped parser. It updates the
bind-mounted file in place, validates Caddy while the old `current` symlink is
still active, then switches the symlink and reloads. A reload failure restores
both the prior Caddyfile and the prior symlink. It retains the active release
plus seven previous releases and the newest eight QAZ-only Caddy backups.

The artifact versions local CSS and JavaScript URLs, so a browser cannot combine
new HTML with stale assets. If an older release replaced the host Caddyfile
atomically, restart the named Caddy container once to attach the current mount,
then verify the product-specific public marker again.

## Boundaries

- Static content only; do not add credentials or private source material.
- The data layer remains local until a public API contract is explicitly owned.
- A local preview or a successful Caddy reload is not public acceptance.
