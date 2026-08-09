#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

python3 scripts/check_static_site.py
node --check app.js
node --check industry.js
node --check industry-data.js
git diff --check
