#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

python3 -m py_compile scripts/*.py
for script in *.js; do
  node --check "$script"
done
bash -n scripts/*.sh
git diff --check
