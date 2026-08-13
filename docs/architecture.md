# Архитектура

## Системная граница

QAZ.INDUSTRIES — статический frontend с локальным слоем reviewed snapshots.
Репозиторий содержит HTML, CSS, JavaScript, JSON/GeoJSON, проверки и release
скрипты. Серверная runtime-составляющая — общий public-sites Caddy, который
отдаёт неизменяемый release tree и добавляет product-specific release marker.

```mermaid
flowchart LR
  subgraph Sources[Внешние публичные источники]
    QZ[QZ.Energy]
    SPACE[Qazaqstan.Space]
    FARM[QAZ.FARM]
    FISH[QAZ.FISH]
    LAKE[QazLake public API]
    GEO[QazGeo public API]
  end
  subgraph Review[Review boundary]
    REF[refresh scripts]
    SNAP[versioned reviewed snapshots]
    MAN[product manifest and release contract]
  end
  subgraph Repo[QAZ checkout]
    HTML[HTML pages]
    SHELL[site-shell.js / app.js]
    CORE[runtime.js / snapshot-contracts.js]
    PROFILE[profile-view.js / industry.js]
    MAP[qazgeo-geometry.js / qazgeo-map.js]
    CSS[styles.css / avds-tokens.css / avds.css]
    DATA[industry-data.js]
    TEST[scripts/check.sh and tests]
  end
  subgraph Runtime[Public runtime]
    CADDY[shared Caddy]
    SITE[immutable current release]
    HEALTH[/api/health and /release.json]
  end
  QZ --> REF
  SPACE --> REF
  FARM --> REF
  FISH --> REF
  LAKE --> REF
  GEO --> REF
  REF --> SNAP
  SNAP --> MAN
  MAN --> TEST
  HTML --> SITE
  SHELL --> SITE
  CORE --> SITE
  PROFILE --> SITE
  MAP --> SITE
  CSS --> SITE
  DATA --> SITE
  SNAP --> SITE
  TEST --> SITE
  SITE --> CADDY
  CADDY --> HEALTH
```

## Поток данных

1. Refresh scripts читают публичные upstream endpoints или link metadata.
2. Без `--write` результат остаётся проверочным output; запись snapshot —
   отдельное review-действие.
3. `scripts/check.sh` проверяет schema, freshness, ссылки, routes, JavaScript,
   unit tests и generated release artifact.
4. `scripts/build_release.py` создаёт release-specific artifact и receipt.
5. Deploy меняет только QAZ-блок и release marker общего Caddyfile, после чего
   public evidence сверяется с source SHA.

## Границы frontend-модулей

- `runtime.js` владеет экранированием, HTTPS URL, versioned asset URL и
  same-origin JSON transport.
- `snapshot-contracts.js` проверяет каждую публичную проекцию до рендера.
- `site-shell.js` владеет темой, мобильной навигацией и focus restoration;
  `app.js` содержит только фильтр главной страницы.
- `profile-view.js` владеет представлением; `industry.js` — состоянием,
  выбором профиля и параллельной загрузкой reviewed snapshots.
- `qazgeo-geometry.js` является чистым модулем проекции; `qazgeo-map.js`
  отвечает только за DOM, keyboard selection и zoom.
- `avds-tokens.css` содержит токены и product aliases, `avds.css` — компоненты
  и публичные паттерны, `styles.css` — layout продукта.

## Доверительные зоны

- **Untrusted upstream** — внешние ответы могут быть недоступны, неполны или
  измениться; они не становятся browser data напрямую.
- **Reviewed projection** — локальный JSON/GeoJSON с provider, timestamp,
  ограничениями и schema version.
- **Public browser** — читает только static assets same-origin.
- **Shared runtime** — отдаёт release и security headers; общий Caddy не
  является продуктовым хранилищем данных.

## Отказ и деградация

При недоступности источника refresh/check должны завершаться ошибкой либо
показывать явный `degraded`/`contract_only`. Нельзя заменять неизвестные данные
нулём, декоративной геометрией или прогнозом. QazGeo GeoJSON используется как
территориальная основа; QazLake не вызывается из браузера.

## Хранилища и зависимости

В checkout нет базы данных, очереди, Docker/Compose или административной панели.
Основные внешние зависимости — публичные сайты-поставщики, QazLake, QazGeo,
GitHub Actions и общий Caddy. AVDS и локализация подключены как source-owned
контракты; platform.qdev.run, EdPol и QAZ.TAX наблюдаются через публичные
контракты и ссылки, но не вызываются из browser runtime. Точный владелец VPS и
staging environment в репозитории не определены; public runtime подтверждается
отдельно.
