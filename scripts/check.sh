#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

python3 scripts/check_static_site.py
python3 scripts/check_routes.py
python3 scripts/check_public_contracts.py
python3 -m py_compile scripts/refresh_qazlake_snapshot.py
python3 -m py_compile scripts/refresh_qazgeo_snapshot.py
python3 -m py_compile scripts/refresh_qazgeo_layer_registry.py
python3 -m py_compile scripts/check_routes.py
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'
node scripts/check_data_contract.mjs
node --check app.js
node --check qazgeo-map.js
node --check industry.js
node --check industry-data.js
check_release="check-$(git rev-parse --short=12 HEAD)"
check_root="$(mktemp -d -t qaz-industries-check.XXXXXX)"
check_build="${check_root}/release"
trap 'rm -rf "$check_root"' EXIT
python3 scripts/build_release.py --release "$check_release" --output "$check_build"
python3 scripts/verify_release_artifact.py --directory "$check_build" --release "$check_release" --commit "$(git rev-parse HEAD)"
git diff --check
