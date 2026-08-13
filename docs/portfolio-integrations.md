# Интеграции портфеля

Упоминание продукта или ссылка на него не означает работающую runtime
интеграцию. Статусы ниже разделяют link metadata, локальную projection и
публично проверенный release.

| Поставщик | Потребитель | Что передаётся | Контракт | Runtime-статус | Приватность | Отказ | Владелец evidence |
|---|---|---|---|---|---|---|---|
| QazGeo | QAZ.INDUSTRIES | reviewed region GeoJSON и layer metadata | `qaz-industries-qazgeo-*`, `qazgeo-layer/v1` | public-verified static snapshot; browser не ходит к API | region precision; sensitive coords исключены | degraded/contract-only | QazGeo + QAZ owner |
| QazLake | QAZ.INDUSTRIES | 3 macro indicators | `qaz-industries-qazlake-public-snapshot-v1` | public-verified static snapshot; direct browser access запрещён | raw observations и private fields исключены | regional/water `degraded` | QazLake + QAZ owner |
| QZ.Energy | QAZ.INDUSTRIES | link metadata и curated profile projection | thematic release + link/source registry | release `qz-energy-avds4-polish-20260813T130000Z` сверен 2026-08-13 | исходный реестр не копируется | source unavailable → monitor failure; последний проверенный срез остаётся видимым | QZ.Energy/QAZ owner |
| Qazaqstan.Space | QAZ.INDUSTRIES | link metadata и curated profile projection | `/data/v1/index.json` + link/source registry | release `2026-08-06.48`, 32 entities, 143 claims и 116 sources сверены 2026-08-10 | только публичные метаданные ссылок | stale contract → monitor failure | Qazaqstan.Space/QAZ owner |
| QAZ.FARM | QAZ.INDUSTRIES | link metadata и curated profile projection | thematic release + link/source registry | release `2026-08-11.3`, 35 entities и 58 sources сверены 2026-08-13 | только публичные метаданные ссылок | transient unavailable → monitor failure без перезаписи среза | QAZ.FARM/QAZ owner |
| QAZ.FISH | QAZ.INDUSTRIES | link metadata и curated profile projection | thematic release + link/source registry | release `2026-08-13.01` сверен 2026-08-13; water upstream не переносится | sensitive points и private data исключены | water catalogue `degraded` | QAZ.FISH/QAZ owner |
| AV DS 4 | QAZ frontend | закреплённый `@sgeo/ui-kit@4.6.0` token export, `avds-tokens.css`, components и compositions через `avds.css` | static package consumer | source-confirmed/local-tested; hashes и local deviations в AVDS system contract | no data transfer | stale package/receipt, missing token/class или неверный порядок → check failure | QAZ frontend owner |
| QazStack manifest | QAZ.INDUSTRIES | product boundary, module declarations и fail-closed consumer inputs | `qazstack-thematic-product-v1`, `qazstack-consumer-contract-v1` | local-tested; оба контракта входят в release artifact | explicit public prohibitions | invalid module/asset → release gate failure | QazStack/QAZ owner |
| platform.qdev.run | QAZ.INDUSTRIES | только наблюдение health/catalog и навигационная связь | public catalog/health | health отвечает; отдельная регистрация QAZ.INDUSTRIES в просмотренном каталоге не найдена | no data transfer | отсутствие регистрации не маскируется под runtime integration | platform/QAZ owner |
| Локализация и переводы | QAZ frontend | локальный RU/KK/EN каталог и runtime contract | `content/locale-contract.v1.json` + `data/ui-locale.v1.json` | source-confirmed; 846 исходных строк, 3 локали, без внешнего translation API | proper names, URLs и units stable | missing catalog → RU fallback/degraded state | QAZ frontend owner |
| EdPol | QAZ.INDUSTRIES | только reviewed link metadata к публичным AVDS/operations receipts | `https://edpol.pro/avds-adoption.json`, `https://edpol.pro/operations-roster.json` | public-observed contract; AVDS 4.7.0, 100%; runtime data transfer не подтверждён | no data transfer | не считать публичные receipts consumer integration | EdPol/QAZ owner |
| QAZ.TAX | QAZ.INDUSTRIES | только reviewed link metadata к публичной AVDS receipt | `https://qaz.tax/.well-known/avds-adoption.json` | public-observed contract; AVDS 4.7.0, 100%; runtime data transfer не подтверждён | no data transfer | не считать публичную receipt data upstream | QAZ.TAX/QAZ owner |
| QazPipe, media и прочие продукты | — | подтверждённой передачи нет | unknown | unknown; не выдавать за integration | unknown | owner/evidence отсутствуют | owner decision required |

Машинный источник этой матрицы — [`data/portfolio-integration-registry.v1.json`](../data/portfolio-integration-registry.v1.json).
Он фиксирует только подтверждённые отношения и отдельно показывает публичные
контракты, которые ещё не являются runtime-потребителями. `scoped_surfaces` не
является процентом зрелости: это счётчик проверенных границ на дату
`evaluated_at` в реестре.

Внешние карточки вроде QazGeo или Qaz.FUND на главной — навигационные ссылки,
если они не перечислены в source registry и не имеют machine contract.
