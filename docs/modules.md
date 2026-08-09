# Каталог модулей

Модуль — пользовательская или контрактная ответственность, описанная через
назначение и поток данных. Состояния `ready`, `partial`, `gap`, `degraded` и `contract_only` не
взаимозаменяемы.

| Модуль | Назначение | Основные входы | Выход | Потребители | Fail-closed |
|---|---|---|---|---|---|
| `profile-registry` | список четырёх отраслевых профилей и link metadata | `data/industry-profiles.v1.json`, `industry-data.js` | профиль, source, release | главная, profile route | неизвестный sector не выбирается |
| `industry-indicators` | KPI и показатели с периодом и ссылкой | curated `industry-data.js` | таблица показателей | `industry.html` | пустой/неполный профиль маркируется |
| `change-pulse` | макро-контекст QazLake | `data/qazlake-public-snapshot.v1.json` | 3 индикатора или degraded | profile pulse | regional/water gaps не заполняются |
| `source-provenance` | происхождение и права link metadata | `data/reviewed-source-registry.v1.json` | source cards и registry | profile, audit | source без HTTPS/rights review отклоняется |
| `territorial-context` | 20 региональных границ и coverage | QazGeo snapshot + GeoJSON | SVG map, territory cards | home, profile | invalid snapshot не рендерится |
| `geo-layer-registry` | перечень шести QazGeo layer contracts | `data/qazgeo-public-layer-registry.v1.json` | layer cards и statuses | profile | `contract_only` остаётся metadata-only |

## Не являющиеся модулями

В checkout нет admin/operator routes, очередей, событийной шины, server-side
API, private data store или отдельной системы авторизации. `benchmarks.html` —
исследовательская страница, а не data ingestion module.

## Карта ответственности

- `index.html` и `app.js` отвечают за вход, фильтры, тему и навигацию.
- `industry.html`, `industry.js` отвечают за профиль, сравнение и snapshot
  modules.
- `qazgeo-map.js` отвечает только за проверенный региональный GeoJSON.
- `avds.css` и `styles.css` отвечают за визуальный consumer layer.
- `scripts/refresh_*.py` готовят snapshots; они не являются runtime API.
- `scripts/check_*.py`, `check_data_contract.mjs` и unit tests — quality gates.

## Общие инварианты

Каждый публичный показатель должен иметь значение, единицу, период, контекст и
HTTPS source URL. Каждый snapshot должен иметь schema version, status, provider,
retrieved timestamp и ограничения. Отсутствие данных обозначается явно.
