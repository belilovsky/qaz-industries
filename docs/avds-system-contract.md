# Системный контракт AVDS4

Этот документ фиксирует фактическую зрелость AVDS4 в QAZ.INDUSTRIES. Он не
подменяет продуктовую готовность и не считает класс в CSS реализованным, пока
нет доказательства использования и проверки. Машиночитаемый источник —
[`data/avds-system-contract.v1.json`](../data/avds-system-contract.v1.json), а
публичный результат — [`data/avds-coverage.v1.json`](../data/avds-coverage.v1.json).

## Как читать показатель

`AVDS 4.6.0-N` в footer — общий показатель из десяти категорий ниже. Он не
равен route coverage. Внутри него отдельно хранится базовый маршрутный контракт
`12/12`: все четыре публичные страницы получают package runtime, токены,
компоненты, shell и зарегистрированные композиции. Текущий `N` — `100%`
(`128/128`): screen-reader, zoom acceptance, периодное сравнение, visual
regression и полный RU/KK/EN интерфейс закрыты отдельными доказательствами.

Каждая категория состоит из именованных требований. Засчитывается только
`verified`; `missing`, `partial`, `planned` и `not-applicable` не повышают
числитель. Скрипт `python3 scripts/check_avds_coverage.py` сверяет route
контракт, provenance, sha256 подключённых файлов, набор категорий, доказательства
и итоговую арифметику. `--write` обновляет только derived receipt после
осознанного изменения system contract.

## 1. Версия и происхождение

Источник фиксирует точную версию `@sgeo/ui-kit`, исходный package revision,
revision control plane, дату синхронизации, SHA-256 runtime/token/component/
layout/consumer файлов и список локальных отклонений. Проверяемый tarball и
его export дополнительно закреплены в
[`data/avds-package-runtime.v1.json`](../data/avds-package-runtime.v1.json).

Отклонения не скрываются: QAZ.INDUSTRIES использует статический CSS adapter,
имеет предметную сетку и aliases; для статического adapter-поверхности
утверждены Chromium baselines 320/1440px и отдельный visual-diff gate.
При обновлении AVDS сначала
нужно обновить tarball и lockfile, запустить `node scripts/build_avds_package.mjs`,
проверить hashes и category evidence, затем обновить receipt и пройти полный
`scripts/check.sh`.

## 2. Токены, шрифты, иконки и темы

Утверждённые сейчас token groups: semantic colors, типографика, интервалы,
радиусы, тени, motion, control sizes, z-index, breakpoints, container widths и
grid gutters — в `avds-tokens.css`. Значения не должны дублироваться в
component layer: `--av-size-control-*`, `--av-z-*`, `--av-breakpoint-*`,
`--av-container-*` и `--av-grid-gutter-*` служат единственной точкой изменения.

Все шесть тем (`institutional`, `editorial`, `data-analytics`, `map`, `dark`,
`print`) имеют token blocks и входят в цикл runtime; `golden-paper` остаётся
дополнительным продуктовым вариантом. Гарнитуры: system sans, Georgia/Times New Roman для headings,
system mono для code; внешние fonts запрещены. Inline icon catalog, размеры,
glyph names и лицензия закреплены в `data/avds-icon-catalog.v1.json`.

## 3. Компонентный контракт

Проверенные компоненты: `av-button`, `av-card`, `av-badge`, `av-chip`,
`av-alert`, `av-table`, `av-form-control`, `av-nav` и `av-menu-button`.
`av-form-control` применяется только к нативным controls внутри подписанного
`label`; `av-nav` — к именованной `nav`; `av-menu-button` всегда имеет
`aria-controls` и управляет элементом с `hidden`. Базовый HTML API — блок,
`__element` и `--variant`, без селекторов, зависящих от внутреннего текста.

Размеры контролов берутся из `--av-size-control-*`; visible focus и disabled
входят в общий API. Вложенность ограничена нативной семантикой: интерактивный
элемент не вкладывается в другой интерактивный элемент. Menu keyboard contract:
открытие переводит фокус в первую ссылку, `Escape` закрывает menu и возвращает
фокус кнопке. Полный inline icon catalog, размеры, glyph names и правила
доступности проверяются `scripts/check_icon_catalog.py`.

## 4. Композиции и состояния

Подтверждены: app shell, footer, паспорт объекта, отраслевой каталог,
аналитическая панель, таблица, фильтры, карта со списком, график с источником,
publication policy, evidence/source cards и methodology/provenance. Их
маршрутные roles фиксируются в route ledger.

На текущем сайте доказаны hover, focus, active, selected, disabled, loading,
skeleton, empty, error, degraded, success, offline, stale data и
`contract-only`: карта и QazLake/QazGeo modules публикуют `data-av-state`, а
layer registry не выдаёт контракт за наблюдение.

## 5. Адаптивная модель

Модель для 320, 390, 768, 820, 1024, 1440, 1920 и 2560px закреплена в
`data/avds-responsive-contract.v1.json`. Она описывает порядок re-composition,
плотность, rails, line length и правило пустот; static gate проверяет token и
CSS prerequisites. Каждая UI-правка требует browser acceptance этих viewports:
ни один маршрут не должен давать горизонтальный overflow.

## 6. Визуализация данных

Карта имеет keyboard controls, текстовый статус, безопасный fallback и
табличные/карточечные альтернативы. Provenance и статус данных выводятся рядом
с public projections. Палитры, шкалы, легенды, оси, единицы, точность и
периодные сравнения закреплены в
`data/avds-data-visualization-contract.v1.json` и проверяются отдельным gate.

## 7. Доступность и контент

Проверяются landmarks, skip link, accessible names, ARIA links, visible focus,
reduced motion и управление картой/меню с клавиатуры. Screen-reader semantic
audit закреплён в `data/avds-accessibility-contract.v1.json`, а 200% zoom/reflow
матрица — в `data/avds-zoom-proof.v1.json`. Контраст и сложные состояния имеют
отдельные gates.

Основной язык — RU; словарь запрещает внутренние англоязычные термины. KK и EN
переключаются через локальный same-origin каталог `data/ui-locale.v1.json` и
`locale.js`; каталог содержит inventory всех четырёх маршрутов, публичных
метаданных и динамических состояний. Нормы чисел, дат, единиц, переносов и
сообщений empty/error проверяются для всех трёх локалей.

## 8. Контроль качества

`scripts/check.sh` включает system/route contract, responsive contract, route
ledger, static, accessibility, content, data и release gates. Route ledger
перечисляет все четыре страницы, их composition roles, состояния и обязательные
viewport. State matrix закрыта frontend tests, а восемь утверждённых screenshot
baselines 320/1440px и dependency-free visual diff находятся в
`data/avds-visual-regression.v1.json` и `tests/visual-baselines/`. При обновлении
AVDS запрещено менять файл/версию без обновления provenance, hashes, evidence,
responsive/a11y proof, visual baselines и полного локального check.
