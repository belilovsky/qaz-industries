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

scp -q "$archive_path" "${remote_host}:/tmp/qaz-industries-${release_id}.tar.gz"
ssh -o BatchMode=yes "$remote_host" bash -s -- "$runtime_root" "$container_name" "$release_id" "$expected_release" <<'REMOTE'
set -euo pipefail
runtime_root="$1"
container_name="$2"
release_id="$3"
expected_release="$4"
archive_path="/tmp/qaz-industries-${release_id}.tar.gz"
release_dir="${runtime_root}/releases/${release_id}"
caddyfile="/opt/qdev-public-sites/Caddyfile"

test "$(readlink "${runtime_root}/current")" = "releases/${expected_release}"
test ! -e "$release_dir"
test -f "$archive_path"
mkdir -p "$release_dir"
tar -xzf "$archive_path" -C "$release_dir"
for asset in index.html industry.html benchmarks.html styles.css avds.css app.js industry-data.js industry.js favicon.svg release.json; do
  test -s "${release_dir}/${asset}"
done

ln -s "releases/${release_id}" "${runtime_root}/.current-next"
mv -Tf "${runtime_root}/.current-next" "${runtime_root}/current"

backup_path="${caddyfile}.qaz-industries-${expected_release}.bak"
cp "$caddyfile" "$backup_path"
caddy_candidate="$(mktemp "${caddyfile}.qaz-industries.XXXXXX")"
sed -E \
  -e "s/(X-Qaz-Release \")[^\"]+(\")/\\1${release_id}\\2/" \
  -e "s/(\"service\":\"qaz-industries\",\"release\":\")[^\"]+(\"})/\\1${release_id}\\2/" \
  "$caddyfile" > "$caddy_candidate"
# Keep the bind-mounted Caddyfile inode stable: Docker otherwise keeps serving
# the old mounted file even though the host path has been atomically replaced.
cat "$caddy_candidate" > "$caddyfile"
rm -f "$caddy_candidate"

rollback() {
  cat "$backup_path" > "$caddyfile"
  ln -s "releases/${expected_release}" "${runtime_root}/.current-rollback"
  mv -Tf "${runtime_root}/.current-rollback" "${runtime_root}/current"
  docker exec "$container_name" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1 || true
}

if ! docker exec "$container_name" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null; then
  rollback
  exit 1
fi
if ! docker exec "$container_name" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null; then
  rollback
  exit 1
fi
rm -f "$archive_path"
printf '%s\n' "$release_id"
REMOTE

printf 'Deployed candidate: %s\n' "$release_id"
