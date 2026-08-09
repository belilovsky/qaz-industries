# QAZ.INDUSTRIES operations

## Ownership

This repository is the source of truth for the static QAZ.INDUSTRIES surface.
The public runtime is an isolated release tree under the shared public-sites
Caddy instance. Its proxy configuration is shared infrastructure: change only
the QAZ.INDUSTRIES release marker, never replace the whole Caddyfile or touch
HAProxy for a content-only release.

## Release procedure

1. Run `scripts/check.sh`.
2. Commit the reviewed source.
3. Run `scripts/deploy.sh` from a clean worktree.
4. Verify the exact release in the response header and `/api/health`.
5. Verify `index.html`, `industry.html?sector=farm`, `benchmarks.html`,
   `styles.css`, `avds.css`, and both JavaScript files over the public domain.
6. Perform a browser pass at desktop and 390px before accepting the release.

The deploy script creates a new immutable release directory, retains previous
releases, backs up Caddy before its marker update, validates the configuration,
and rolls back the symlink/configuration on an in-script validation failure. It
updates the bind-mounted Caddyfile in place so a normal reload reads the new
configuration. If an older release replaced that host file atomically, restart
the named Caddy container once to attach the current mount, then verify the
public release marker again. It also versions local CSS and JavaScript URLs in
the release artifact, so a browser cannot combine new HTML with stale assets.

## Boundaries

- Static content only; do not add credentials or private source material.
- The data layer remains local until a public API contract is explicitly owned.
- A local preview or a successful Caddy reload is not public acceptance.
