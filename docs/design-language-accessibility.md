# Дизайн, язык и доступность

## AV DS 4

QAZ.INDUSTRIES — consumer AV DS 4, а не владелец замещающей библиотеки. Токены
и темы находятся в `avds-tokens.css`, компоненты и паттерны — в `avds.css`.
Публичные поверхности используют `av-button`, `av-card`,
`av-badge`, `av-alert`, `av-chip`, `av-table`, а также композиции public export,
source registry, geo-layer registry и related questions. Изменения токенов и
компонентов должны сохранять `data-design-system="avds4"` на трёх страницах.

Неиспользуемые классы AV DS не считаются реализованными только потому, что они
есть в CSS. Текущие потребители подтверждаются HTML/JS и static checker.

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
`scripts/check_accessibility.py` проверяет эти структурные правила на всех трёх
маршрутах. Печать и отдельная 404-страница пока не входят в публичный route set.

## Безопасное состояние

Loading, unavailable, degraded и contract-only состояния должны иметь текстовое
объяснение и ссылку на источник/ограничение. Нельзя скрывать отсутствие данных
пустой карточкой или декоративной картой.
