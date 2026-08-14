# Безопасность, приватность и правовые границы

## Классы данных

- **Public reviewed** — HTML, CSS, JS, reviewed JSON/GeoJSON, source links,
  release identity.
- **Source metadata** — provider, revision, dates, URLs, coverage and
  limitations; публикуются только после review.
- **Sensitive/excluded** — raw QazLake observations, private identifiers,
  exact user locations, sensitive infrastructure coordinates, credentials,
  private queues и непроверенные entity matches.

В текущем frontend нет аккаунтов, форм с персональными данными, cookies для
аналитики, внешнего tracking или пользовательского хранилища. Consent и
retention для пользовательских данных не применяются, пока такие функции не
появятся; добавление их требует отдельного review.

Аналитика отключена как продуктовое решение, а не как незавершённая настройка.
QAZ не заявляет посещаемость, конверсию или retention без отдельного измеряемого
контракта и правил согласия.

## Доверительные границы

Untrusted upstream → reviewed static snapshot → same-origin browser → shared
Caddy. Browser не вызывает QazLake/QazGeo напрямую. Caddy скрывает `.env`, `.git`,
deploy/config/log/script файлы и отдаёт только QAZ release.

## Runtime safeguards

Public runtime выставляет HSTS, nosniff, Referrer-Policy, SAMEORIGIN,
Permissions-Policy, строгий CSP, COOP/CORP и product-specific release header.
`/api/health` и `/release.json` имеют `Cache-Control: no-store`. Динамический
рендеринг экранирует текст и принимает только HTTPS links и известные states.

## Запреты публикации

Не публиковать private source material, credentials, raw lake records, точные
чувствительные координаты, данные детей/уязвимых групп, неразрешённые media
assets или кандидатов как проверенные факты. Не считать OSM/QazGeo слой
инженерным, юридическим или оперативным реестром.

## Инциденты и доступ

Подозрение на уязвимость направляется через
[GitHub Security Advisories](https://github.com/belilovsky/qaz-industries/security/advisories/new)
с URL, минимальным воспроизведением и impact; публичный issue не используется.
Отчёты о shared proxy/VPS должны явно указывать границу QAZ. Доступ к VPS,
Caddy и source registry не документируется credentials-ами.

GitHub private vulnerability reporting включён для этого публичного репозитория
и является устойчивым публично указанным private intake. Публичный security
mailbox не требуется; публичный issue для уязвимостей запрещён.

## Права, атрибуция и хранение

- Собственные тексты, интерфейс и код не считаются открыто лицензированными,
  если рядом с конкретным asset не указана отдельная лицензия.
- Права на внешние наборы остаются у поставщиков. Link metadata и проверенная
  проекция не передают право на исходный набор.
- OSM-derived layers публикуются с `© OpenStreetMap contributors` и ссылкой на
  ODbL 1.0; они не считаются официальным инженерным или правовым реестром.
- Runtime хранит активный и семь предыдущих immutable release trees, а также
  восемь последних QAZ-only Caddy backups. Monitor artifacts хранятся 7 дней.
- Предыдущие release trees нужны только для отката и не являются публичным
  архивом. Спорный материал удаляется из текущего выпуска новым release.

Публичная версия этих правил находится на `/publication.html`.

## Оставшийся вопрос

До появления формы, аккаунта или intake пользовательские данные не собираются.
Если такой функционал будет добавлен, для него до разработки нужны отдельные
consent, retention и deletion rules. Устойчивый приватный security contact
настроен.
