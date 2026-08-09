# Contributing

Keep changes scoped to QAZ.INDUSTRIES and preserve the static/public boundary.
Before opening a change, run `scripts/check.sh`; it checks the AV DS surface,
data schema, safe Caddy patch contract, JavaScript syntax, and a generated
release artifact.

For a release, commit the reviewed source and deploy only from a clean
worktree. A public release is accepted only when its custom response header,
`/api/health`, immutable `release.json`, key assets, and a browser pass agree.
