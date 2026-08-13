# Маршруты и интерфейсы

Машинные интерфейсы и пользовательские страницы разделены. В checkout нет
административного API, очередей, RSS, embed API, Web Components или websocket.

## Пользовательские маршруты

| URL | Назначение | Состояния |
|---|---|---|
| `/` | обзор, фильтры, две QazGeo maps, входы в профили | карта loading/degraded/ready, theme, mobile menu |
| `/industry.html?sector=energy` | профиль энергетики | 4 supported sector values; unknown value falls back to energy |
| `/industry.html?sector=space` | профиль космической отрасли | тот же профильный shell |
| `/industry.html?sector=farm` | профиль сельского хозяйства | тот же профильный shell |
| `/industry.html?sector=water` | профиль водоёмов и рыболовства | water gaps явно отображаются |
| `/benchmarks.html` | исследовательские референсы и matrix | статический материал |
| `/publication.html` | происхождение, права, retention и исправления | статическая политика публикации |

Канонический public route set закреплён в `scripts/check_routes.py` и
`sitemap.xml`. Query parameter `sector` не создаёт новый server route.

## Runtime endpoints

| Endpoint | Ответ | Cache | Доказательство |
|---|---|---|---|
| `/api/health` | `{status, service, release}` | `no-store` | Caddy fragment, public probe |
| `/release.json` | `{service, release, commit}` | `no-store` | generated release, public probe |

Оба endpoint принадлежат release runtime, а не frontend data layer. Они не
принимают пользовательские параметры и не раскрывают credentials.

## Публичные data contracts

`data/industry-profiles.v1.json`, `data/qazlake-public-snapshot.v1.json`,
`data/qazgeo-public-snapshot.v1.json`, `data/qazgeo-regions-public.v1.geojson`,
`data/qazgeo-public-layer-registry.v1.json`,
`data/reviewed-source-registry.v1.json`,
`data/portfolio-integration-registry.v1.json` и
`data/qaz-industries-thematic-release.v1.json`, а также корневой
`qazstack-consumer.json` — versioned static assets.
Schema, provider, freshness и ограничения описаны в
[`data-provenance.md`](data-provenance.md).

## Browser interactions

- главная: filter chips, theme toggle, menu, map zoom/reset/selection;
- профиль: sector switch, source links, comparison selects, snapshot statuses;
- все динамические значения проходят escaping и принимают только HTTPS links и
  известные states.

`site-shell.js` не содержит логики конкретного route. `runtime.js` и
`snapshot-contracts.js` образуют общий fail-closed boundary; profile/map
контроллеры получают только same-origin release assets.

События не отправляются во внешнюю аналитику. Очередей и фоновых consumer-ов в
этом проекте нет.

## Локализация и совместимость

HTML использует `lang="ru"`; отдельные `kk` и `en` bundles отсутствуют. Query
values `energy`, `space`, `farm`, `water` являются текущим совместимым набором.
Изменение идентификаторов требует обновления HTML, JS, data contract и sitemap.

## Безопасность интерфейсов

Все внешние ссылки используют HTTPS и открываются с `rel="noreferrer"`. Caddy
задаёт строгий CSP без внешних script/style/font источников. Прямой browser
access к QazLake/QazGeo запрещён архитектурой.
