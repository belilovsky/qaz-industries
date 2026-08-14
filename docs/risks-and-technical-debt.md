# Ограничения, риски и технический долг

| Риск | Evidence | Состояние | Следующее действие |
|---|---|---|---|
| QazStack consumer contract | `qazstack-consumer.json` + local contract gate | controlled | сохранять module parity с manifest |
| Профильные release labels | Energy/Space/Farm/Fish machine/public releases и 23 ссылки сверены 2026-08-10 | controlled | daily sector probe; не обновлять без проверенного источника |
| QazLake regional/water отсутствует | snapshots явно `degraded` | planned/blocked | ждать публичного контракта, не синтезировать значения |
| QazGeo OSM-derived layers требуют attribution | layer registry + `/publication.html` | controlled | сохранять `© OpenStreetMap contributors` и ODbL link |
| Нет отдельного staging | release script проверяет artifact и Caddy candidate до switch | accepted | использовать atomic release + rollback; не заявлять staging |
| Browser proof должен обновляться на каждом release | `docs/current-release.md` содержит desktop/mobile, console и overflow receipt | controlled | перезаписывать receipt только после новой публичной проверки |
| Runtime owner | QAZ release owner + shared public-sites operator | controlled/role-based | добавить приватный escalation contact вне public docs |
| Нет аналитики и traction | `/publication.html`, source inventory | accepted | аналитика отключена; не заявлять investor metrics |
| Security contact | GitHub private vulnerability reporting enabled | controlled | keep the advisory route visible and do not accept vulnerability reports in public issues |
| Публичный runtime | release `20260810T055834Z-311cd246bba4`, health/release/header/browser proof | controlled | сохранять atomic deploy, bounded retention и public acceptance |
| Несколько ignored work ledgers | `work/` excluded by `.gitignore` | historical/local-only | не считать их durable source of truth |

## Non-negotiable limits

Не превращать contract-only в observation, не публиковать private/raw data, не
выдавать административную геометрию за объектный реестр, не считать HTTP 200
доказательством качества данных и не менять соседние портфельные checkout.
