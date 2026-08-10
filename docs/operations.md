# Эксплуатация QAZ.INDUSTRIES

## Владелец и граница runtime

Репозиторий — источник статической public surface. Runtime находится в
изолированном release tree под shared public-sites Caddy. Caddyfile является
общей инфраструктурой: изменяется только блок `qaz.industries` и его
`X-Qaz-Industries-Release`. Нельзя заменять весь Caddyfile, менять общий
`X-Qaz-Release` или трогать HAProxy для content-only выпуска.

Владелец репозитория выполняет роль QAZ release owner; оператор shared
public-sites Caddy/VPS — runtime owner. Отдельного staging-домена нет: принятая
граница — локальный immutable artifact, проверенный Caddy candidate, атомарный
switch и rollback. Это осознанная схема выпуска, а не заявление о наличии
staging.

## Процедура выпуска

1. Сохранить Git status, remote и source SHA.
2. Выполнить read-only refresh QazLake, QazGeo и layer registry:
   `python3 scripts/refresh_qazlake_snapshot.py`,
   `python3 scripts/refresh_qazgeo_snapshot.py`,
   `python3 scripts/refresh_qazgeo_layer_registry.py`.
   Затем выполнить `python3 scripts/check_sector_sources.py` для четырёх
   отраслевых release markers и всех ссылок профилей.
3. Проверить каждый diff; `contract_only` может менять metadata, но не может
   стать выдуманным observation.
4. Запустить `scripts/check.sh`.
5. Зафиксировать reviewed source и собрать immutable release.
6. Только владелец выпуска запускает `scripts/deploy.sh` из clean worktree.
7. Проверить header, `/api/health`, `/release.json`, ключевые assets и public
   browser states.
8. Принять выпуск только когда source, artifact, runtime и public evidence
   согласуются.

Commit и deploy не являются частью локальной проверки документации.

## Immutable release и rollback

Deploy создаёт новую release directory и до переключения `current` проверяет
продуктовый Caddy parser. При ошибке reload восстанавливаются предыдущий
Caddyfile и symlink. Хранятся активный release, семь предыдущих release и восемь
последних QAZ-only Caddy backups. Artifact версионирует локальные CSS/JS URLs,
чтобы HTML и assets не смешивались.

Если digest host/container Caddyfile не совпадает или bind mount не получил
candidate, deploy останавливается до смены symlink. После ручной замены host
Caddyfile сначала восстанавливается parity, затем повторяется выпуск.

## Public verification

Минимальный набор:

```bash
curl -fsS https://qaz.industries/api/health
curl -fsSI https://qaz.industries/
curl -fsS https://qaz.industries/release.json
curl -fsS https://qaz.industries/robots.txt
curl -fsS https://qaz.industries/sitemap.xml
```

Browser proof проверяет desktop и 390px для home, profile, benchmarks и
publication,
console errors, overflow, menu/theme/filter/compare/map interactions и release
identity. HTTP 200 или успешный Caddy reload сами по себе не являются public
acceptance.

## Monitor и границы

`.github/workflows/public-contract-monitor.yml` работает read-only, ежедневно
в 03:17 UTC и сохраняет probe artifacts на семь дней; он не коммитит snapshots и
не деплоит. Local preview, workflow green и Caddy reload не заменяют public
proof.

Публичная surface статична. Не добавлять credentials, private source material,
raw QazLake data или прямой browser access к upstream. CSP остаётся strict;
licensed local fonts допускаются только после отдельного rights review и
проверки byte parity.
