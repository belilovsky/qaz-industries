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

`public-contract-monitor.yml` ежедневно запускает независимые read-only probes
для QazLake, QazGeo, layer registry и четырёх отраслевых продуктов, а
`scripts/check.sh` выполняется независимо от результата upstream. Artifact с
каждым результатом и aggregate summary сохраняется 7 дней. Недоступный QazLake
получает `degraded`, пока последний reviewed snapshot не старше 31 дня;
повреждённый или stale snapshot, QazGeo failure и sector drift блокируют
workflow. Monitor не коммитит, не публикует и не переключает runtime.

## Диагностика

```bash
curl -fsS https://qaz.industries/api/health
curl -fsSI https://qaz.industries/
curl -fsS https://qaz.industries/release.json
scripts/check.sh
```

Если release header, health и `release.json` различаются, выпуск считается
непринятым. QazLake outage допускает только bounded degraded state со snapshot
не старше 31 дня; stale или invalid snapshot блокирует выпуск. Если Caddy parity
не проходит, deploy должен остановиться до смены активного symlink.

## Наблюдаемые пробелы

В репозитории нет alert routing, SLO dashboard, error aggregation, browser
telemetry или публичного uptime history. Роли владельцев определены как owner
QAZ release и оператор shared public-sites runtime; конкретный приватный канал
эскалации не публикуется. Срок хранения monitor artifacts — 7 дней.
