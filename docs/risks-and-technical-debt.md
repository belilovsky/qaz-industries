# Ограничения, риски и технический долг

| Риск | Evidence | Состояние | Следующее действие |
|---|---|---|---|
| Отсутствует `qazstack-consumer.json` | manifest path не существует в checkout | blocked | подтвердить внешний контракт или убрать ссылку владельцем |
| Профильные release labels устарели | upstream страницы новее локальных labels | blocked/review | обновить только после owner/source review |
| QazLake regional/water отсутствует | snapshots явно `degraded` | planned/blocked | ждать публичного контракта, не синтезировать значения |
| QazGeo OSM-derived layers требуют attribution | layer registry | owner decision | утвердить licence/attribution wording |
| Нет staging evidence | checkout и public endpoints | unknown | определить staging owner или явно зафиксировать отсутствие |
| Browser proof не хранится как tracked receipt | roadmap/ignored work ledgers | historical | вести current release receipt с viewport/console/overflow |
| Runtime owner не назван поимённо | operations говорит shared Caddy | unknown | добавить владельца и escalation path без credentials |
| Нет аналитики и traction | source inventory | unknown | не заявлять investor metrics до измерения |
| Локальная projection не синхронизируется автоматически | `industry-data.js` | source-confirmed | добавить review cadence, не прямой browser ingestion |
| Несколько ignored work ledgers | `work/` excluded by `.gitignore` | historical/local-only | не считать их durable source of truth |

## Non-negotiable limits

Не превращать contract-only в observation, не публиковать private/raw data, не
выдавать административную геометрию за объектный реестр, не считать HTTP 200
доказательством качества данных и не менять соседние портфельные checkout.
