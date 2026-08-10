# Текущий статус выпуска

Дата проверки: **2026-08-10, Asia/Almaty**. Это канонический receipt последнего
публичного выпуска QAZ.INDUSTRIES; локальные проверки, runtime identity и
публичная браузерная приёмка разделены ниже.

## Identity

| Поле | Значение | Достоверность |
|---|---|---|
| Project | QAZ.INDUSTRIES | source-confirmed |
| Checkout | `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries` | source-confirmed |
| Remote | `https://github.com/belilovsky/qaz-industries.git` | source-confirmed |
| Branch | `main` | source-confirmed |
| Deployed source SHA | `311cd246bba4539303c09006fc1535ba547682b7` | source/runtime/public-confirmed |
| Remote `origin/main` | `12f27b3396594e4a05bc2a5039b6b601fe736245` | remote-confirmed; release commits intentionally not pushed |
| Public domain | [https://qaz.industries/](https://qaz.industries/) | public-verified |
| Runtime | shared public-sites Caddy, immutable release + `current` symlink | runtime-confirmed |
| Public release | `20260810T055834Z-311cd246bba4` | runtime/public-confirmed |

Функциональный commit `311cd246bba4…` является точным источником публичного
артефакта. Этот receipt фиксируется последующим documentation-only commit,
поэтому локальный `HEAD` может быть новее deployed source SHA. Push не
выполнялся.

## Local acceptance

- `scripts/check.sh` прошёл перед commit и повторно внутри deploy: static,
  routes, accessibility, русская терминология, quality budgets, документация,
  публичные контракты и immutable artifact — `OK`.
- Выполнено 11 Python-тестов и 9 Node-тестов. Добавлен регрессионный контракт,
  запрещающий AV DS 4 повторно показывать элементы с `hidden`.
- Network drift probe подтвердил четыре upstream release ID и 23 профильные
  ссылки: Energy `35dbd1d`, Space `2026-08-06.48`, Farm `2026-08-10.1`, Fish
  `2026-08-09.03`.
- Qazaqstan.Space теперь проверяется через `/data/v1/index.json`, а не через
  зависимый от текста главной страницы HTML-regex.

## Runtime acceptance

- `scripts/deploy.sh` принял чистый commit, повторил gate и собрал immutable
  release `20260810T055834Z-311cd246bba4`.
- Кандидат Caddy прошёл marker check и `caddy validate`; после атомарного
  переключения `current` mounted config, release identity и host/container
  digests были проверены повторно.
- Runtime receipt: `releases=8`, `backups=8`, `release_kib=704`. Rollback
  остаётся привязан к предыдущему immutable release.

## Public acceptance

- [release.json](https://qaz.industries/release.json) и
  [api/health](https://qaz.industries/api/health) возвращают один release;
  apex отвечает HTTP 200, HTTP и `www` перенаправляются 301 на HTTPS apex.
- CSP, HSTS, `nosniff`, frame/referrer/permissions и COOP/CORP headers
  присутствуют. Четыре ключевых публичных файла побайтно совпали с source.
- Все 36 проверяемых URL — страницы, четыре sector state, CSS/JS, discovery,
  QazStack contracts и public data assets — вернули HTTP 200.
- Playwright проверил все семь пользовательских состояний на 1280×800 и
  390×844. Горизонтального overflow, duplicate IDs, незавершённых loading
  states, console warnings/errors и page errors нет.
- Главная показывает две карты и 40 реальных SVG-геометрий QazGeo. Фильтры
  теперь действительно показывают 4/1/1/6 карточек; inspector карты, смена
  темы, сравнение профилей и мобильное меню с возвратом фокуса работают.
- Farm показывает актуальный выпуск `2026-08-10.1`, 35 сущностей и 57
  источников. Остальные три профиля сохранили подтверждённые release IDs.

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
- Scheduled monitor реализован и локально проверен, но не активен в GitHub,
  пока release commits намеренно остаются без push.

Эти blockers не нарушают текущую публичную работоспособность, но не позволяют
заявлять наблюдаемые данные или операционные каналы, которых ещё нет.
