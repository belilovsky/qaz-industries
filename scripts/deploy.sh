#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

remote_host="${QAZ_INDUSTRIES_HOST:-root@srv1829804.hstgr.cloud}"
runtime_root="${QAZ_INDUSTRIES_RUNTIME_ROOT:-/opt/qdev-public-sites/www/qaz.industries}"
container_name="${QAZ_INDUSTRIES_CADDY_CONTAINER:-qdev-public-sites-proxy}"

if [ -n "$(git status --porcelain)" ]; then
  echo "Refusing to deploy a dirty worktree." >&2
  exit 1
fi

commit_short="$(git rev-parse --short=12 HEAD)"
release_id="$(date -u +%Y%m%dT%H%M%SZ)-${commit_short}"
expected_release="$(ssh -o BatchMode=yes "$remote_host" "readlink '${runtime_root}/current' | sed 's#^releases/##'")"

case "$expected_release" in
  *[!A-Za-z0-9_-]*|'') echo "Invalid active release marker from runtime." >&2; exit 1 ;;
esac

scripts/check.sh
build_dir="$(python3 scripts/build_release.py --release "$release_id")"
archive_path="$(mktemp -t qaz-industries-release.XXXXXX.tar.gz)"
trap 'rm -f "$archive_path"' EXIT
COPYFILE_DISABLE=1 tar --no-xattrs -C "$build_dir" -czf "$archive_path" .

remote_archive_path="/tmp/qaz-industries-${release_id}.tar.gz"
remote_patch_path="/tmp/qaz-industries-patch-${release_id}.py"
scp -q "$archive_path" "${remote_host}:${remote_archive_path}"
scp -q scripts/patch_caddy_release.py "${remote_host}:${remote_patch_path}"
ssh -o BatchMode=yes "$remote_host" bash -s -- "$runtime_root" "$container_name" "$release_id" "$expected_release" "$remote_archive_path" "$remote_patch_path" <<'REMOTE'
set -euo pipefail
runtime_root="$1"
container_name="$2"
release_id="$3"
expected_release="$4"
archive_path="$5"
patch_path="$6"
release_dir="${runtime_root}/releases/${release_id}"
caddyfile="/opt/qdev-public-sites/Caddyfile"

test "$(readlink "${runtime_root}/current")" = "releases/${expected_release}"
test ! -e "$release_dir"
test -f "$archive_path"
test -f "$patch_path"
mkdir -p "$release_dir"
tar -xzf "$archive_path" -C "$release_dir"
for asset in index.html industry.html benchmarks.html styles.css avds.css app.js industry-data.js industry.js favicon.svg release.json; do
  test -s "${release_dir}/${asset}"
done

backup_path="${caddyfile}.qaz-industries-${release_id}.bak"
cp "$caddyfile" "$backup_path"
caddy_candidate="$(mktemp "${caddyfile}.qaz-industries.XXXXXX")"
container_candidate="/tmp/Caddyfile.qaz-industries-${release_id}"
cleanup() {
  rm -f "$archive_path" "$patch_path" "$caddy_candidate"
  docker exec "$container_name" rm -f "$container_candidate" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# This parser fails closed unless there is exactly one QAZ block and changes
# only that block. It must never touch generic X-Qaz-Release headers owned by
# other public sites in this shared file.
python3 "$patch_path" --input "$caddyfile" --output "$caddy_candidate" --release "$release_id"
# Validate the candidate inside the Caddy container before the bind-mounted
# shared source file changes at all.
docker cp "$caddy_candidate" "${container_name}:${container_candidate}"
if ! docker exec "$container_name" caddy validate --config "$container_candidate" --adapter caddyfile >/dev/null; then
  exit 1
fi
# Keep the bind-mounted Caddyfile inode stable: Docker otherwise keeps serving
# the old mounted file even though the host path has been atomically replaced.
cat "$caddy_candidate" > "$caddyfile"

rollback() {
  cat "$backup_path" > "$caddyfile"
  ln -s "releases/${expected_release}" "${runtime_root}/.current-rollback"
  mv -Tf "${runtime_root}/.current-rollback" "${runtime_root}/current"
  docker exec "$container_name" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1 || true
}

if ! docker exec "$container_name" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null; then
  cat "$backup_path" > "$caddyfile"
  exit 1
fi

# Validate the shared config before the public release pointer changes. This
# prevents a syntactically-invalid marker from exposing a new static tree.
test "$(readlink "${runtime_root}/current")" = "releases/${expected_release}"
ln -s "releases/${release_id}" "${runtime_root}/.current-next"
mv -Tf "${runtime_root}/.current-next" "${runtime_root}/current"
if ! docker exec "$container_name" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null; then
  rollback
  exit 1
fi

# Retain the active release plus seven previous immutable releases and the
# eight newest QAZ-only Caddy backups. Names are generated from validated
# release IDs, and the scope never extends outside this product's directories.
mapfile -t old_releases < <(
  find "${runtime_root}/releases" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' \
    | sort -r | tail -n +9
)
for old_release in "${old_releases[@]}"; do
  case "$old_release" in
    *[!A-Za-z0-9_-]*|'') exit 1 ;;
  esac
  rm -rf -- "${runtime_root}/releases/${old_release}"
done
mapfile -t old_backups < <(
  find "$(dirname "$caddyfile")" -mindepth 1 -maxdepth 1 -type f -name 'Caddyfile.qaz-industries-*.bak' -printf '%f\n' \
    | sort -r | tail -n +9
)
for old_backup in "${old_backups[@]}"; do
  case "$old_backup" in
    Caddyfile.qaz-industries-*[!A-Za-z0-9_.-]*|Caddyfile.qaz-industries-) exit 1 ;;
  esac
  rm -f -- "$(dirname "$caddyfile")/${old_backup}"
done
printf '%s\n' "$release_id"
REMOTE

printf 'Deployed candidate: %s\n' "$release_id"
