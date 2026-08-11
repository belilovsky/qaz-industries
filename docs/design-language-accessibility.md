# Дизайн, язык и доступность

## AV DS 4

QAZ.INDUSTRIES — consumer AV DS 4, а не владелец замещающей библиотеки. Токены
и темы находятся в `avds-tokens.css`, компоненты и паттерны — в `avds.css`.
Публичные поверхности используют `av-button`, `av-card`,
`av-badge`, `av-alert`, `av-chip`, `av-table`, а также композиции public export,
source registry, geo-layer registry и related questions. Изменения токенов и
компонентов должны сохранять `data-design-system="avds4"` на четырёх страницах.

Неиспользуемые классы AV DS не считаются реализованными только потому, что они
есть в CSS. Текущие потребители подтверждаются HTML/JS и static checker.

Публичный footer показывает машиночитаемую версию и покрытие в формате
`AVDS 4.x.x-N`. Источник — `data/avds-coverage.v1.json`; `N` вычисляется как
доля пройденных consumer-adoption gates, а не как доля всего каталога
компонентов. Команда `python3 scripts/check_avds_coverage.py --write` обновляет
gate states и шильдик, обычный `scripts/check.sh` отклоняет устаревший receipt.

Shell gate включает все четыре страницы: header, основная и мобильная
навигация, actions и footer имеют отдельные AV DS composition roles. Это
статическая адаптация спокойного application shell: продуктовая сетка и бренд
остаются локальными, а размеры интерактивных целей, active state, focus и
семантика ролей закреплены AV DS слоем.

Consumer registration закреплена взаимным контрактом `avds-consumer.json` и
записью `qaz_industries` в control-plane AV DS. Режим интеграции остаётся
`static-contract`: пакет `@sgeo/ui-kit@4.6.0` закреплён локальным проверяемым
артефактом, а его официальный export токенов собирается в
`avds-package-runtime.css`. Продуктовый token layer подключается следом и
сохраняет локальные aliases; React и дополнительный JavaScript не добавляются.
`scripts/build_avds_package.mjs --check` сверяет версию, tarball, export и
runtime digest до каждого полного gate и выпуска.

## Язык и терминология

Основной язык интерфейса — русский (`lang="ru"`). Словарь
`content/terminology.ru.json` и `scripts/check_content.py` запрещают возврат
внутренних англоязычных формулировок в пользовательские поверхности. Официальные названия QazGeo,
QazLake, AV DS 4 и продуктов портфеля сохраняются. Нельзя смешивать русский и
английский в одном понятии без причины; при первом использовании редкого
сокращения нужно дать расшифровку. Казахская и английская локализация пока не
реализованы.

## Типографика и темы

Цвета, интервалы, радиусы и состояния тем задаются `avds-tokens.css`; layout
продукта находится в `styles.css`.
Переключатель темы и `prefers-reduced-motion` должны сохранять читаемость,
контраст и видимый focus. Внешние fonts не загружаются.

## Accessibility contract

Требуются skip links, semantic headings, labels, visible focus, keyboard map
selection/zoom, `aria-live` для snapshot statuses, `aria-pressed` для filters и
`role` только по назначению. Mobile target — 390px без горизонтального overflow.
`scripts/check_accessibility.py` проверяет эти структурные правила на всех
четырёх маршрутах. Печать и отдельная 404-страница пока не входят в публичный route set.

## Безопасное состояние

Loading, unavailable, degraded и contract-only состояния должны иметь текстовое
объяснение и ссылку на источник/ограничение. Нельзя скрывать отсутствие данных
пустой карточкой или декоративной картой.
