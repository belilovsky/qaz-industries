# Текущий статус выпуска

Дата проверки: **2026-08-13, Asia/Almaty**. Это канонический receipt последнего
публичного выпуска QAZ.INDUSTRIES; локальные проверки, runtime identity и
публичная браузерная приёмка разделены ниже.

## Identity

| Поле | Значение | Достоверность |
|---|---|---|
| Project | QAZ.INDUSTRIES | source-confirmed |
| Checkout | `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries` | source-confirmed |
| Remote | `https://github.com/belilovsky/qaz-industries.git` | source-confirmed |
| Branch | `main` | source-confirmed |
| Deployed source SHA | `6af819cb58dbe8e860376e6ad09d67d5be4a7449` | source/runtime/public-confirmed |
| Remote `origin/main` at code deploy | `6af819cb58dbe8e860376e6ad09d67d5be4a7449` | remote-confirmed |
| Public domain | [https://qaz.industries/](https://qaz.industries/) | public-verified |
| Runtime | shared public-sites Caddy, immutable release + `current` symlink | runtime-confirmed |
| Public release | `20260813T111745Z-6af819cb58db` | runtime/public-confirmed |

Функциональный commit `6af819c…` является точным источником публичного
артефакта. Release переключён атомарно после проверки Caddy bind mount,
контейнера и public smoke. Последующие documentation-only commits могут сделать
локальный и удалённый `HEAD` новее deployed source SHA, не меняя публичные
исполняемые файлы.

## Local acceptance

- `scripts/check.sh` прошёл перед commit и повторно внутри deploy: AVDS package
  runtime, AVDS coverage, static, routes, accessibility, русская терминология,
  quality budgets, документация, публичные контракты и immutable artifact —
  `OK`.
- Выполнено 11 Python-тестов и 10 Node-тестов; все прошли.
- Отдельная network-сверка `scripts/check_sector_sources.py` прошла по 23
  внешним ссылкам: QZ.Energy `qz-energy-avds4-polish-20260813T130000Z`,
  Qazaqstan.Space `2026-08-06.48`, QAZ.FARM `2026-08-11.3` и QAZ.FISH
  `2026-08-13.01`.
- Coverage receipt подтверждает общий AVDS system contract `128/128` (**100%**),
  а базовый route/consumer contract — `12/12` (**100%**), badge
  `AVDS 4.6.0-100`. Полный локальный UI-каталог содержит 846 исходных строк
  в трёх локалях (`ru-RU`, `kk-KZ`, `en-US`); переключение языков проверено
  браузером, включая динамический industry-профиль и график.
- `@sgeo/ui-kit@4.6.0` закреплён vendored tarball с SHA-256
  `2e8382b74019e5fda6cd56bdbc58ec4864819825276828f6a235487d2d48a77c`;
  официальный token export детерминированно собирается в
  `avds-package-runtime.css` и проверяется по digest.
- Полный AVDS control-plane gate также прошёл: typecheck, hygiene, contracts,
  52 основных и 8 budget-тестов.
- Реестр интеграций фиксирует 12 scoped surfaces: 9 contract/snapshot-backed,
  2 публичных link-only receipts (EdPol и QAZ.TAX) и 1 наблюдаемую платформу без
  найденной машинной регистрации (`platform.qdev.run`).

## Runtime acceptance

- `scripts/deploy.sh` принял чистый commit, повторил все gates и собрал
  immutable release `20260813T111745Z-6af819cb58db`.
- Кандидат Caddy прошёл marker check и `caddy validate`; после атомарного
  переключения `current` публичные release identity и health проверены снова.
- Host и bind-mounted Caddyfile совпадают (`/opt/qdev-public-sites/Caddyfile` ↔
  `/qdev-public-sites/Caddyfile`); `/etc/caddy/Caddyfile` не используется.
- Runtime receipt: `releases=8`, `backups=8`, `release_kib=1172`. Rollback
  остаётся привязан к предыдущему immutable release.

## Public acceptance

- [release.json](https://qaz.industries/release.json) и
  [api/health](https://qaz.industries/api/health) возвращают один release и
  точный source SHA `6af819cb58dbe8e860376e6ad09d67d5be4a7449`; все четыре
  страницы, AVDS runtime CSS, locale catalog и consumer contract отвечают
  HTTP 200.
- [AVDS coverage receipt](https://qaz.industries/data/avds-coverage.v1.json)
  публично подтверждает общий `128/128` и `100%`, route/consumer `12/12` и
  `100%`, badge `AVDS 4.6.0-100`; package runtime receipt подтверждает версию,
  tarball/export/artifact digests и отсутствие добавленного JavaScript.
- CSP, HSTS, `nosniff`, frame/referrer/permissions и COOP/CORP headers
  присутствуют; ответ содержит точный `X-QAZ-Industries-Release`.
- Playwright проверил четыре страницы на 320, 390, 768, 820, 1024, 1440,
  1920 и 2560px: в 32 route×viewport комбинациях asset marker `6af819cb58db`,
  badge свежий, четыре AVDS stylesheet подключены в правильном порядке,
  горизонтального overflow и page/console errors нет. Дополнительно проверены `en-US` и `kk-KZ`, меню и
  Escape/focus-поведение; industry route содержит 4 snapshot rows, 14 chart
  rows и одну period comparison, data states остаются success/contract-only по
  источнику.
- Мобильное меню открывается, передаёт фокус первой ссылке, закрывается по
  `Escape` и возвращает фокус кнопке; console warnings/errors отсутствуют.
- [Реестр интеграций](https://qaz.industries/data/portfolio-integration-registry.v1.json)
  отвечает `200` и содержит подтверждённые upstream revisions QazLake
  `3490a750dfc2b2a1454db842d1b342f608705ade` и QazGeo
  `d05cde433e96808f8afac9a2a6510e237c023f26`, а также receipts EdPol/QAZ.TAX.
- Legacy request `GET /favicon.ico` отвечает `308` на локальный
  `/favicon.svg`; прямой JSON-маршрут реестра в браузере имеет `application/json`
  и не создаёт console errors.

## Portfolio integration receipt

Машинный контракт и границы: [`data/portfolio-integration-registry.v1.json`](../data/portfolio-integration-registry.v1.json).

| Surface | Current relation | Evidence |
|---|---|---|
| AVDS 4 / QazStack / translations | source-verified local contracts | pinned AVDS 4.6.0, QazStack consumer, RU/KK/EN catalog |
| QazLake / QazGeo | reviewed same-origin snapshots | revisions above; regional/water gaps remain degraded or contract-only |
| QZ.Energy / Space / FARM / FISH | curated profile projections | four live release IDs listed in local acceptance |
| EdPol / QAZ.TAX | public contract link metadata only | AVDS 4.7.0 adoption receipts, no runtime data transfer |
| platform.qdev.run | health/catalog observed, no registration found | public health `434e97db5e62186ca5907c7d8ca325035dee892b` |

## Data boundary

Браузер читает только versioned same-origin reviewed projections. Raw QazLake,
закрытые очереди, учётные данные и чувствительные координаты не публикуются.
Отсутствующие региональные и водные наблюдения остаются `degraded`, а
`contract_only` не превращается в наблюдение или нулевое значение.

## Открытые внешние blockers

- QazLake regional indicators и water catalogue ожидают публичного upstream
  contract; сайт корректно работает в fail-closed degraded state.
- Стабильный приватный security intake отсутствует: private vulnerability
  reporting в GitHub не включён и публичный mailbox не назначен.

Эти внешние blockers не нарушают текущую публичную работоспособность и не
снижают AVDS consumer coverage, но не позволяют заявлять отсутствующие данные
или операционные каналы.
