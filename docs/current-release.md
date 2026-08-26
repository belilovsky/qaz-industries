# Текущий статус выпуска

Дата runtime-проверки: **2026-08-23, Asia/Almaty**. Этот документ описывает
текущий публичный выпуск. Новый local candidate после этой даты не считается
опубликованным, пока не получит отдельный immutable release identity.

## Identity

| Поле | Значение | Достоверность |
|---|---|---|
| Project | QAZ.INDUSTRIES | source-confirmed |
| Checkout | `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries` | source-confirmed |
| Remote | `https://github.com/belilovsky/qaz-industries.git` | source-confirmed |
| Branch | `main` | source-confirmed |
| Deployed source SHA | `7cb44a040c2de1baef0a604d59b1a4b738a8d4dc` | source/runtime/public-confirmed |
| Public domain | [https://qaz.industries/](https://qaz.industries/) | public-verified |
| Runtime | shared public-sites Caddy, immutable release + `current` symlink | runtime-confirmed |
| Public release | `20260823T134657Z-7cb44a040c2d` | runtime/public-confirmed |

`release.json`, `/api/health` and `X-QAZ-Industries-Release` называют один
выпуск. Caddy marker, host/container mount parity и immutable release tree
проверены внутри guarded deploy.

## Local acceptance for the released source

- `bash scripts/check.sh` прошёл перед выпуском: package/runtime, AVDS system
  contract, responsive/route/static/accessibility gates, locale, content,
  data/privacy, public contracts и immutable artifact.
- Прошли 16 Python и 11 Node tests; release artifact contract — `OK`.
- `@sgeo/ui-kit@4.6.0` закреплён vendored tarball с SHA-256
  `2e8382b74019e5fda6cd56bdbc58ec4864819825276828f6a235487d2d48a77c`.
- AVDS receipt выпуска: `126/128` (**98%**), route contract `11/12` (**92%**),
  badge `AVDS 4.6.0-98`. External consumer registration не засчитана без
  inspectable control-plane source receipt.
- RU/KK/EN каталог содержит 845 source strings и не вызывает translation API
  в браузере. Динамический AVDS badge локализуется через same-origin catalog;
  русские процентные формы вычисляются по правилам склонения.

## Public proof

- Live-public Playwright matrix прошла `8/8`: четыре canonical routes на 390 и
  1440 CSS pixels, без горизонтального overflow, console/CSP blocker или page
  error. Evidence: `output/playwright/live-20260823T134657Z-7cb44a040c2d/`;
  `sourceSha` и `runtimeSha` равны опубликованному SHA выше.
- Все четыре canonical routes, AVDS consumer и Platform registration request
  получили HTTP `200`. Главная страница также проверена с корректными title,
  landmarks, QazGeo map controls и AVDS badge.
- Отдельная local-candidate matrix также прошла `8/8` после исправления
  локализованной грамматики шильдика. Это доказательство исходника и не меняет
  публичный immutable release identity.

## Data and integration boundaries

Браузер читает только versioned same-origin reviewed projections. Raw QazLake,
закрытые очереди, учётные данные и чувствительные координаты не публикуются.
Региональные и водные пробелы остаются `degraded`/`contract_only`.

Platform catalog/schema public probes redirect to authenticated HTML; поэтому
`qdev-project.json` не фабрикуется. Точный owner, canonical path и closure proof
описаны в [`data/platform-registration-request.v1.json`](../data/platform-registration-request.v1.json)
и [Platform audit](audits/platform-integration-2026-08-23.md).
