# Интеграции портфеля

Упоминание продукта или ссылка на него не означает работающую runtime
интеграцию. Статусы ниже разделяют link metadata, локальную projection и
публично проверенный release.

| Поставщик | Потребитель | Что передаётся | Контракт | Runtime-статус | Приватность | Отказ | Владелец evidence |
|---|---|---|---|---|---|---|---|
| QazGeo | QAZ.INDUSTRIES | reviewed region GeoJSON и layer metadata | `qaz-industries-qazgeo-*`, `qazgeo-layer/v1` | public-verified static snapshot; browser не ходит к API | region precision; sensitive coords исключены | degraded/contract-only | QazGeo + QAZ owner |
| QazLake | QAZ.INDUSTRIES | 3 macro indicators | `qaz-industries-qazlake-public-snapshot-v1` | public-verified static snapshot; direct browser access запрещён | raw observations и private fields исключены | regional/water `degraded` | QazLake + QAZ owner |
| QZ.Energy | QAZ.INDUSTRIES | link metadata и curated profile projection | thematic release + link/source registry | release `qz-energy-refactor-20260809T184604Z-35dbd1d` сверен 2026-08-10 | исходный реестр не копируется | source unavailable → monitor failure; последний проверенный срез остаётся видимым | QZ.Energy/QAZ owner |
| Qazaqstan.Space | QAZ.INDUSTRIES | link metadata и curated profile projection | public release marker + link/source registry | release `2026-08-06.48` сверен 2026-08-10 | только публичные метаданные ссылок | stale label → monitor failure | Qazaqstan.Space/QAZ owner |
| QAZ.FARM | QAZ.INDUSTRIES | link metadata и curated profile projection | thematic release + link/source registry | release `2026-08-09.15` сверен 2026-08-10; источник периодически недоступен по TLS | только публичные метаданные ссылок | transient unavailable → monitor failure без перезаписи среза | QAZ.FARM/QAZ owner |
| QAZ.FISH | QAZ.INDUSTRIES | link metadata и curated profile projection | thematic release + link/source registry | release `2026-08-09.03` сверен 2026-08-10; water upstream не переносится | sensitive points и private data исключены | water catalogue `degraded` | QAZ.FISH/QAZ owner |
| AV DS 4 | QAZ frontend | tokens через `avds-tokens.css`, components и compositions через `avds.css` | local consumer layer | source-confirmed/local-tested; не shared package runtime | no data transfer | missing token/class или неверный порядок → static check failure | QAZ frontend owner |
| QazStack manifest | QAZ.INDUSTRIES | product boundary, module declarations и fail-closed consumer inputs | `qazstack-thematic-product-v1`, `qazstack-consumer-contract-v1` | local-tested; оба контракта входят в release artifact | explicit public prohibitions | invalid module/asset → release gate failure | QazStack/QAZ owner |
| QazPipe, media и прочие продукты | — | подтверждённой передачи нет | unknown | unknown; не выдавать за integration | unknown | owner/evidence отсутствуют | owner decision required |

Внешние карточки вроде QazGeo или Qaz.FUND на главной — навигационные ссылки,
если они не перечислены в source registry и не имеют machine contract.
