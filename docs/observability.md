# Наблюдаемость и диагностика

## Runtime signals

- `X-Qaz-Industries-Release` — release marker на public responses.
- `/api/health` — no-store JSON с service/status/release.
- `/release.json` — no-store JSON с service/release/commit.
- Caddy security headers — CSP, HSTS, nosniff, COOP/CORP, Permissions-Policy и
  Referrer-Policy.

Эти сигналы подтверждают identity и доступность surface, но не подтверждают
свежесть каждого upstream источника.

## Scheduled monitor

`public-contract-monitor.yml` ежедневно запускает read-only refresh probes для
QazLake, QazGeo и layer registry, затем `scripts/check.sh`. Artifact сохраняется
7 дней. Workflow не коммитит, не публикует и не переключает runtime.

## Диагностика

```bash
curl -fsS https://qaz.industries/api/health
curl -fsSI https://qaz.industries/
curl -fsS https://qaz.industries/release.json
scripts/check.sh
```

Если release header, health и `release.json` различаются, выпуск считается
непринятым. Если snapshot stale или upstream unavailable, сохраняется degraded
state. Если Caddy parity не проходит, deploy должен остановиться до смены
активного symlink.

## Наблюдаемые пробелы

В репозитории нет alert routing, SLO dashboard, error aggregation, browser
telemetry или публичного uptime history. Владелец runtime и срок хранения
monitor artifacts должны быть подтверждены отдельно.
