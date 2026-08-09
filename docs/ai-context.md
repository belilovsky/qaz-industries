# Контекст для ИИ-агентов

## 1. Идентичность и статус

Это QAZ.INDUSTRIES — статический public product о проверяемых индустриях
Казахстана. Канонический checkout и текущая identity находятся в
[`current-release.md`](current-release.md). Не выбирайте соседний проект по
текущему cwd.

## 2. Карта файлов

- HTML: `index.html`, `industry.html`, `benchmarks.html`.
- Frontend: `app.js`, `industry.js`, `qazgeo-map.js`, `theme.js`.
- Profile projection: `industry-data.js`.
- Styles: `styles.css`, `avds.css`.
- Contracts: `qazstack-thematic-product.json`, `data/*.json`, GeoJSON.
- Checks: `scripts/check*.py`, `scripts/check_data_contract.mjs`, `tests/`.
- Release: `scripts/build_release.py`, `scripts/deploy.sh`, `deploy/`.
- Docs: [`docs/index.md`](index.md).

## 3. Что можно публиковать

Только reviewed static projections, source links, dates, units, coverage,
limitations и release identity. Нельзя публиковать raw/private QazLake fields,
credentials, exact sensitive coordinates, private queues или candidate matches.

## 4. Основные потоки

Главная → sector profile → indicators/pulse/layers/chain/geography/coverage/
sources/questions. Profile fetches same-origin snapshots with `no-store`; map
fetches local sanitized GeoJSON. QazLake/QazGeo upstream не вызываются браузером.

## 5. Инварианты

Не синтезировать значения, не подменять unknown нулём, не называть
`contract_only` наблюдением, сохранять period/unit/source, экранировать text,
принимать только HTTPS links, не смешивать local/runtime/public evidence.

## 6. Интеграции

QazGeo и QazLake — reviewed static snapshots; QZ.Energy, Qazaqstan.Space,
QAZ.FARM и QAZ.FISH — source/link metadata и curated profile projections; AV DS 4
— local consumer layer. QazPipe и другие продукты не считать интеграциями без
направления, контракта, владельца и evidence.

## 7. Безопасное изменение

1. Resolve project и continuity check.
2. Сохранить Git status, remote, SHA.
3. Прочитать `docs/index.md`, `current-release.md`, нужный contract.
4. Сформулировать allowlist и done-when.
5. Изменять один bounded slice.
6. Запустить focused check, затем `scripts/check.sh`.
7. Отдельно проверить runtime/public; local green не является public proof.

## 8. Change-impact checklist

- HTML route/sitemap/canonical metadata;
- profile keys и query `sector`;
- data schema, provider, dates, rights, freshness;
- degraded/contract-only states;
- AV DS tokens, ARIA, keyboard, 390px layout;
- source registry and attribution;
- CSP/Caddy boundary;
- release artifact and `release.json` parity;
- docs index, current release and AI context.

## 9. Типовые ошибки

Не редактировать соседний checkout, не читать скриншот как production evidence,
не копировать upstream registry, не добавлять прямой API fetch в browser, не
запускать deploy для локальной проверки, не придумывать license, market size или
traction.

## 10. Запрещённые автоматические действия

Без отдельного разрешения нельзя commit, push, deploy, менять общий Caddyfile,
писать production data, добавлять credentials, отправлять сообщения внешним
владельцам или превращать план в факт.
