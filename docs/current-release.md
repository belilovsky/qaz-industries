# Текущий статус выпуска

Дата проверки: **2026-08-12, Asia/Almaty**. Это канонический receipt последнего
публичного выпуска QAZ.INDUSTRIES; локальные проверки, runtime identity и
публичная браузерная приёмка разделены ниже.

## Identity

| Поле | Значение | Достоверность |
|---|---|---|
| Project | QAZ.INDUSTRIES | source-confirmed |
| Checkout | `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries` | source-confirmed |
| Remote | `https://github.com/belilovsky/qaz-industries.git` | source-confirmed |
| Branch | `main` | source-confirmed |
| Deployed source SHA | `0ed802b8c35b083cc0646a91b83bccae7b597462` | source/runtime/public-confirmed |
| Remote `origin/main` at deploy | `0ed802b8c35b083cc0646a91b83bccae7b597462` | remote-confirmed |
| Public domain | [https://qaz.industries/](https://qaz.industries/) | public-verified |
| Runtime | shared public-sites Caddy, immutable release + `current` symlink | runtime-confirmed |
| Public release | `20260811T192751Z-0ed802b8c35b` | runtime/public-confirmed |

Функциональный commit `0ed802b8c35b…` является точным источником публичного
артефакта. Этот receipt фиксируется последующим documentation-only commit,
поэтому локальный и удалённый `HEAD` могут быть новее deployed source SHA без
расхождения публичных исполняемых файлов.

## Local acceptance

- `scripts/check.sh` прошёл перед commit и повторно внутри deploy: AVDS package
  runtime, AVDS coverage, static, routes, accessibility, русская терминология,
  quality budgets, документация, публичные контракты и immutable artifact —
  `OK`.
- Выполнено 11 Python-тестов и 9 Node-тестов; все прошли.
- Coverage receipt подтверждает 12 из 12 применимых consumer adoption gates:
  **100%**, badge `AVDS 4.6.0-100`.
- `@sgeo/ui-kit@4.6.0` закреплён vendored tarball с SHA-256
  `2e8382b74019e5fda6cd56bdbc58ec4864819825276828f6a235487d2d48a77c`;
  официальный token export детерминированно собирается в
  `avds-package-runtime.css` и проверяется по digest.
- Полный AVDS control-plane gate также прошёл: typecheck, hygiene, contracts,
  52 основных и 8 budget-тестов.

## Runtime acceptance

- `scripts/deploy.sh` принял чистый commit, повторил все gates и собрал
  immutable release `20260811T192751Z-0ed802b8c35b`.
- Кандидат Caddy прошёл marker check и `caddy validate`; после атомарного
  переключения `current` публичные release identity и health проверены снова.
- Runtime receipt: `releases=8`, `backups=8`, `release_kib=728`. Rollback
  остаётся привязан к предыдущему immutable release.

## Public acceptance

- [release.json](https://qaz.industries/release.json) и
  [api/health](https://qaz.industries/api/health) возвращают один release и
  точный source SHA; все четыре страницы, AVDS runtime CSS и consumer contract
  отвечают HTTP 200.
- [AVDS coverage receipt](https://qaz.industries/data/avds-coverage.v1.json)
  публично подтверждает 12/12 и 100%; package runtime receipt подтверждает
  версию, tarball/export/artifact digests и отсутствие добавленного JavaScript.
- CSP, HSTS, `nosniff`, frame/referrer/permissions и COOP/CORP headers
  присутствуют; ответ содержит точный `X-QAZ-Industries-Release`.
- Playwright проверил четыре страницы на 1280×900 и 390×844: в восьми
  комбинациях badge свежий, четыре AVDS stylesheet подключены в правильном
  порядке, горизонтального overflow и page errors нет.
- Мобильное меню открывается, передаёт фокус первой ссылке, закрывается по
  `Escape` и возвращает фокус кнопке; console warnings/errors отсутствуют.

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
