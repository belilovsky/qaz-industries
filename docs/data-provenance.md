# Данные и происхождение

QAZ.INDUSTRIES публикует reviewed static projections. Каждая запись должна
сохранять источник, период, единицу, дату получения и границу вывода. Snapshot
старше 31 дня не проходит public contract check.

## Реестр наборов

| Набор | Источник и способ получения | Охват | Состояние | Потребители и ограничения |
|---|---|---|---|---|
| `industry-profiles.v1.json` | curated link metadata и release labels | 4 профиля | ready | profile registry; labels требуют сверки с upstream |
| `industry-data.js` | локальная curated projection из четырёх отраслевых продуктов | показатели, chain, geography, gaps | ready/partial по профилю | frontend; не является автоматической синхронизацией |
| `qazlake-public-snapshot.v1.json` | `https://qlake.tech/api/economy/indicators`, reviewed static retrieval | 3 макроиндикатора | ready | pulse; региональные показатели и вода `degraded` |
| `qazgeo-public-snapshot.v1.json` | QazGeo health/layers/regions API | 20 регионов, 252 города, 77 646 POI в coverage | ready | territory context; это не отраслевые наблюдения |
| `qazgeo-regions-public.v1.geojson` | sanitized QazGeo GeoJSON | 20 Polygon/MultiPolygon | ready | browser SVG map; точные чувствительные координаты не добавляются |
| `qazgeo-public-layer-registry.v1.json` | reviewed QazGeo layer metadata | 6 layer contracts | 4 stable/observed, 2 `contract_only` | layer registry; contract-only не содержит наблюдений |
| `reviewed-source-registry.v1.json` | human-reviewed link metadata | 6 source IDs | active-link-metadata | provenance cards; не копирует исходные реестры |
| `qaz-industries-thematic-release.v1.json` | generated release contract | 6 module records | release-specific | identity, counts, source IDs, digest |

## Правила lineage

`source-confirmed` означает, что утверждение видно в текущем исходнике или
manifest. `local-tested` означает прохождение локального gate. `runtime-verified`
и `public-verified` требуют отдельной даты, URL и release identity. Старые
release labels — `historical`, пока не сверены с владельцем upstream.

Для каждого набора фиксируются provider, source revision, `retrieved_at`,
`published_at`/`data_as_of`, schema version, scope, freshness и limitations.
Синтетические числа, подстановка нуля вместо unknown и вывод о точном объекте из
административной геометрии запрещены.

## Права и чувствительность

Публичная проекция исключает raw QazLake fields, private identifiers, exact user
locations, sensitive infrastructure coordinates и candidate/entity matches.
Для OpenStreetMap-derived QazGeo layers требуется attribution. Финальная
лицензия публикации QAZ и текст attribution требуют решения владельца.

## Недоступность источника

Refresh/check должны завершаться с ошибкой или сохранять явный degraded state.
Браузер продолжает показывать объяснение границы, но не выдаёт устаревший
snapshot за текущую observation. `contract_only` остаётся описанием интерфейса
до появления наблюдаемого upstream snapshot и review.

## Известные расхождения

Профильные labels в `industry-profiles.v1.json` и `industry-data.js` могут быть
старее публичных страниц Qazaqstan.Space, QAZ.FARM и QAZ.FISH. На проверке
2026-08-09 upstream показывали `2026-08-06.48`, дату `2026-08-09` и structured
updates 2026-08-09 соответственно. Это фиксируется как freshness/review issue,
а не исправляется догадкой внутри документации.

Манифест указывает `qazstack-consumer.json`, но файл отсутствует в checkout.
Пока владелец не подтвердит внешний контракт, ссылка считается `blocked`.
