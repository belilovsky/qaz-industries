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

Подозрение на уязвимость направляется по приватному каналу владельца репозитория,
с URL, минимальным воспроизведением и impact; публичный issue не используется.
Отчёты о shared proxy/VPS должны явно указывать границу QAZ. Доступ к VPS,
Caddy и source registry не документируется credentials-ами.

## Нерешённые правовые вопросы

Владелец должен подтвердить лицензию публикации QAZ, attribution для
OSM-derived layers, retention policy для будущего intake, security contact и
процедуру удаления/исправления публикаций. Пока решения нет, документация
помечает вопрос `blocked`, а не предполагает лицензию.
