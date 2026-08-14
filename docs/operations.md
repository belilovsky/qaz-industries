# Эксплуатация QAZ.INDUSTRIES

## Владелец и граница runtime

Репозиторий — источник статической public surface. Публичный сайт сейчас
доставляется NAS-runtime через shared reverse proxy. Старый Caddy release tree
остался историческим механизмом: он не должен использоваться для нового
content-only выпуска, менять общий Caddyfile или создавать видимость успешного
переключения, когда NAS не обновлён.

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
6. Выпустить build через документированный канал владельца NAS-runtime.
   `scripts/deploy.sh` рассчитан на прежний Caddy runtime и должен завершаться
   fail-closed до появления новой процедуры.
7. Проверить `/api/health`, `/release.json`, ключевые assets и public browser
   states; source SHA, artifact, runtime и public response должны совпасть.
8. Принять выпуск только когда source, artifact, runtime и public evidence
   согласуются.

Commit и deploy не являются частью локальной проверки документации.

## Immutable release и rollback

Старый deploy создавал immutable release tree и атомарно переключал Caddy
symlink. Эта гарантия не переносится автоматически на NAS-runtime. Пока его
владелец не зафиксирует новый release/rollback контракт, содержательный deploy
считается заблокированным: локальная сборка и push не заменяют публичный выпуск.

Новая процедура должна до переключения проверить candidate artifact, сохранить
предыдущую активную версию для отката и после переключения подтвердить exact
source SHA через `/release.json`, `/api/health` и браузерный smoke.

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
