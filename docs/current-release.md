# Текущий статус выпуска

Дата проверки: **2026-08-10, Asia/Almaty**. Сам выпуск создан
**2026-08-09 UTC**. Это единственный документ с текущим разделением
source/runtime/public evidence; исторические планы его не переопределяют.

## Identity

| Поле | Значение | Достоверность |
|---|---|---|
| Project | QAZ.INDUSTRIES | source-confirmed |
| Checkout | `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries` | source-confirmed |
| Remote | `https://github.com/belilovsky/qaz-industries.git` | source-confirmed |
| Branch | `main` | source-confirmed |
| Deployed source SHA | `006421f9b697674adc1f120a9ab19fe61b71a9a1` | source/runtime/public-confirmed |
| Remote `origin/main` | `12f27b3396594e4a05bc2a5039b6b601fe736245` | remote-confirmed; release commits intentionally not pushed |
| Public domain | [https://qaz.industries/](https://qaz.industries/) | public-verified |
| Runtime | shared public-sites Caddy, immutable release + `current` symlink | runtime-confirmed by release script |
| Public release | `20260809T185728Z-006421f9b697` | runtime/public-verified |

Рефакторинг зафиксирован commit `006421f9b697…` и именно из него собран
публичный артефакт. Этот release receipt хранится последующим documentation-only
commit, поэтому локальный `HEAD` может быть новее deployed source SHA. Push не
выполнялся.

## Local acceptance

- `scripts/check.sh` завершён успешно перед commit и повторно внутри deploy:
  static contract, route hygiene, accessibility, русская терминология, quality
  budgets, ссылки 24 документов и публичные data-contracts — `OK`.
- Выполнено 7 Python-тестов и 9 Node-тестов; контракт четырёх профилей и
  immutable release artifact — `OK`.
- Локальная браузерная приёмка проверила исправленные тексты на 1280 px и
  390 px: переполнения, ошибок и предупреждений консоли нет.

## Runtime acceptance

- `scripts/deploy.sh` принял только чистый commit, повторил полный quality gate,
  собрал immutable release и подтвердил `qaz.industries Caddy marker: OK`.
- Кандидат Caddy был проверен до переключения `current`; после переключения
  конфигурация повторно прошла `caddy validate` и reload. В скрипте сохранён
  автоматический rollback на предыдущий release/config при ошибке reload.
- Активирован release `20260809T185728Z-006421f9b697`; соседние checkout и
  публичные данные других продуктов не изменялись.

## Public acceptance

- [release.json](https://qaz.industries/release.json) возвращает release выше и
  полный commit `006421f9b697674adc1f120a9ab19fe61b71a9a1`.
- [api/health](https://qaz.industries/api/health) возвращает `status=ok`, service
  `qaz-industries` и тот же release.
- Apex возвращает HTTP 200 и `X-Qaz-Industries-Release`; `www` перенаправляет
  HTTP 301 на apex. CSP, HSTS, `nosniff`, frame/referrer/permissions и
  cross-origin заголовки присутствуют.
- Главная, четыре sector-state профиля, бенчмарки, три CSS, девять JavaScript
  модулей и четыре ключевых публичных data asset вернули HTTP 200.
- Публичный браузер на 1280 px и 390 px подтвердил: две карты и 40 реальных
  региональных SVG-геометрий, шесть отраслевых входов, профиль с 4 показателями,
  3 макро-карточками, 3 территориальными карточками, 6 слоями и 4 источниками,
  а также 7 бенчмарков и 8 строк матрицы. Горизонтального переполнения,
  console errors и warnings нет; мобильное меню открывается, закрывается по
  Escape и возвращает фокус.

## Data boundary

Браузер читает только версионированные same-origin статические проекции.
Исходные наблюдения QazLake, закрытые очереди, учётные данные и чувствительные
координаты не публикуются. Состояние `upstream_unavailable` остаётся явным:
региональные QazLake-показатели и водные наблюдения не подменяются нулями или
синтетическими значениями.

## Open owner blockers

- `qazstack-consumer.json` указан в манифесте, но отсутствует в checkout.
- Региональные QazLake indicators и water catalogue остаются degraded до
  появления публичного upstream contract.
- QAZ publication licence, окончательная attribution wording, retention policy,
  security contact и именной runtime owner требуют решений владельца.
- Staging URL/owner не определены; production rollback проверяется release
  script, но отдельный staging receipt отсутствует.
