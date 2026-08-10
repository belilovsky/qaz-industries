# Каталог модулей

Модуль — пользовательская или контрактная ответственность, описанная через
назначение и поток данных. Состояния `ready`, `partial`, `gap`, `degraded` и `contract_only` не
взаимозаменяемы.

| Модуль | Назначение | Основные входы | Выход | Потребители | Fail-closed |
|---|---|---|---|---|---|
| `profile-registry` | список четырёх отраслевых профилей и метаданные ссылок | `data/industry-profiles.v1.json`, `industry-data.js` | профиль, источник, выпуск | главная, profile route | неизвестный sector возвращает energy без выдуманного профиля |
| `industry-indicators` | KPI и показатели с периодом и ссылкой | curated `industry-data.js`, `profile-view.js` | таблица показателей | `industry.html` | значения экранируются, ссылка обязана быть HTTPS |
| `change-pulse` | макро-контекст QazLake | `data/qazlake-public-snapshot.v1.json` | 3 индикатора или degraded | profile pulse | regional/water gaps не заполняются |
| `source-provenance` | происхождение и права link metadata | `data/reviewed-source-registry.v1.json` | source cards и registry | profile, audit | source без HTTPS/rights review отклоняется |
| `territorial-context` | 20 региональных границ и coverage | QazGeo snapshot + GeoJSON | SVG map, territory cards | home, profile | invalid snapshot не рендерится |
| `geo-layer-registry` | перечень шести QazGeo layer contracts | `data/qazgeo-public-layer-registry.v1.json` | layer cards и statuses | profile | `contract_only` остаётся metadata-only |

## Не являющиеся модулями

В checkout нет admin/operator routes, очередей, событийной шины, server-side
API, private data store или отдельной системы авторизации. `benchmarks.html` —
исследовательская страница, а не data ingestion module.

## Карта ответственности

- `site-shell.js` отвечает за тему и навигацию, `app.js` — только за фильтры.
- `industry.html`, `profile-view.js`, `industry.js` разделяют разметку,
  представление и управление состоянием профиля.
- `snapshot-contracts.js` отклоняет неверные публичные проекции до рендера.
- `qazgeo-geometry.js` и `qazgeo-map.js` разделяют расчёт путей и DOM карты.
- `avds-tokens.css`, `avds.css` и `styles.css` разделяют токены, компоненты и layout.
- `scripts/public_snapshot.py` и `scripts/refresh_*.py` готовят snapshots; они не
  являются runtime API.
- `qazstack-consumer.json` связывает те же шесть module IDs с публичными
  asset-ами, allowed states и fail-closed политикой; gate требует полного
  совпадения с manifest.
- `scripts/check_*.py`, `check_data_contract.mjs` и unit tests — quality gates.

## Общие инварианты

Каждый публичный показатель должен иметь значение, единицу, период, контекст и
HTTPS source URL. Каждый snapshot должен иметь schema version, status, provider,
retrieved timestamp и ограничения. Отсутствие данных обозначается явно.
