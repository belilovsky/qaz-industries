# Интеграции портфеля

Упоминание продукта или ссылка на него не означает работающую runtime
интеграцию. Статусы ниже разделяют link metadata, локальную projection и
публично проверенный release.

| Поставщик | Потребитель | Что передаётся | Контракт | Runtime-статус | Приватность | Отказ | Владелец evidence |
|---|---|---|---|---|---|---|---|
| QazGeo | QAZ.INDUSTRIES | reviewed region GeoJSON и layer metadata | `qaz-industries-qazgeo-*`, `qazgeo-layer/v1` | public-verified static snapshot; browser не ходит к API | region precision; sensitive coords исключены | degraded/contract-only | QazGeo + QAZ owner |
| QazLake | QAZ.INDUSTRIES | 3 macro indicators | `qaz-industries-qazlake-public-snapshot-v1` | public-verified static snapshot; direct browser access запрещён | raw observations и private fields исключены | regional/water `degraded` | QazLake + QAZ owner |
| QZ.Energy | QAZ.INDUSTRIES | link metadata и curated profile projection | link/source registry; отдельного ingestion API нет | local/static projection; public source link | исходный реестр не копируется | stale label или source unavailable → review | QZ.Energy/QAZ owner |
| Qazaqstan.Space | QAZ.INDUSTRIES | link metadata и curated profile projection | link/source registry; отдельного ingestion API нет | local/static projection; текущий upstream release требует сверки | only public link metadata | stale label → historical/review | Qazaqstan.Space/QAZ owner |
| QAZ.FARM | QAZ.INDUSTRIES | link metadata и curated profile projection | link/source registry; отдельного ingestion API нет | local/static projection; текущий upstream release требует сверки | only public link metadata | stale label → historical/review | QAZ.FARM/QAZ owner |
| QAZ.FISH | QAZ.INDUSTRIES | link metadata и curated profile projection | link/source registry; отдельного ingestion API нет | local/static projection; water upstream не переносится | sensitive points и private data исключены | water catalogue `degraded` | QAZ.FISH/QAZ owner |
| AV DS 4 | QAZ frontend | tokens, components и compositions через `avds.css` | local consumer layer | source-confirmed/local-tested; не shared package runtime | no data transfer | missing class → static check failure | QAZ frontend owner |
| QazStack manifest | QAZ.INDUSTRIES | product boundary и module declarations | `qazstack-thematic-product-v1` | local/source-confirmed; `qazstack-consumer.json` отсутствует | explicit public prohibitions | contract link `blocked` | QazStack/QAZ owner |
| QazPipe, media и прочие продукты | — | подтверждённой передачи нет | unknown | unknown; не выдавать за integration | unknown | owner/evidence отсутствуют | owner decision required |

Внешние карточки вроде QazGeo или Qaz.FUND на главной — навигационные ссылки,
если они не перечислены в source registry и не имеют machine contract.
