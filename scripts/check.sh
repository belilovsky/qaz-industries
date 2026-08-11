#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

node scripts/build_avds_package.mjs --check
python3 scripts/check_avds_coverage.py
python3 scripts/check_static_site.py
python3 scripts/check_routes.py
python3 scripts/check_accessibility.py
python3 scripts/check_content.py
python3 scripts/check_quality_budgets.py
python3 scripts/check_docs.py
python3 scripts/check_public_contracts.py
python3 -m py_compile scripts/*.py
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'
node scripts/check_data_contract.mjs
node --test tests/*.test.cjs
for script in *.js; do node --check "$script"; done
bash -n scripts/check.sh scripts/deploy.sh
check_release="check-$(git rev-parse --short=12 HEAD)"
check_root="$(mktemp -d -t qaz-industries-check.XXXXXX)"
check_build="${check_root}/release"
trap 'rm -rf "$check_root"' EXIT
python3 scripts/build_release.py --release "$check_release" --output "$check_build"
python3 scripts/verify_release_artifact.py --directory "$check_build" --release "$check_release" --commit "$(git rev-parse HEAD)"
git diff --check
