# Двусторонний reuse-аудит QAZ.INDUSTRIES

Статус: `source-confirmed` для локального кандидата; не является release или
публичным runtime proof. Основание исходников — QAZ.INDUSTRIES
`e30f7079238298952b332ae94f0e35ec330391f8`; канонический QazStack —
`081de3852ce0becbbc408272fcaa925fc4cf4117`. PR #99 имеет head
`222f2bafda76a774fb8202113277eb1895e2c664` и не является канонической
центральной регистрацией до обычного merge и отдельного provider proof.

## Решения

- Сохраняются два уже корректных QazStack reuse: `thematic-product-contracts`
  и `reviewed-source-registry`. Центральная consumer registration из PR #99 —
  отдельный незавершённый registry step, а не новая продуктовая зависимость.
- QZ.Energy дал только безопасный паттерн machine discovery. В продукте создан
  собственный генератор [`data/public-discovery.v1.json`](../../data/public-discovery.v1.json)
  → [`ai-index.json`](../../ai-index.json), [`llms.txt`](../../llms.txt): он
  принимает исключительно локальный allowlist. Код, snapshots и отраслевые
  данные QZ.Energy не переносятся.
- QZ.Energy и Qazaqstan.Space остаются федеративными ссылочными provenance
  contract-ами через reviewed source registry. Их snapshots не становятся
  входом QAZ.INDUSTRIES.
- Atlas Qazaq Family не импортируется. Для отраслевого продукта остаются свои
  санитизированные QazGeo snapshots с точной ревизией и fail-closed проверкой.
- QazStack temporal diff отложен: для него нужны два сопоставимых исторических
  snapshots и назначенный release owner.

## Обратное переиспользование

Отраслевые модели, статические данные и release/deploy checks остаются
продуктовыми. Открыта только P1 discovery-запись `reviewed-static-snapshot`:
нейтральный build-time contract для schema, freshness, digest и fail-closed
status потенциально полезен QAZ.INDUSTRIES, QZ.Energy и Qazaqstan.Space, но
не извлекается и не публикуется без подтверждённого одинакового контракта,
второго потребителя и owner approval QazStack.

Паттерн санитизации 20 регионов и geometry checks направляется владельцу
QazGeo. Он может стать QazGeo-owned public projection только при двух
подтверждённых потребителях. Состояния loading/offline/degraded не выносятся
в QazStack: их семантика — контракт продукта, а визуальная реализация — AVDS.

## Отдельные линии доказательств

| Линия | Текущий вывод |
|---|---|
| Source | baseline QAZ и QazStack зафиксированы выше; machine discovery локально генерируется и проверяется. |
| Provider CI | `unverifiable`: в этом локальном reuse-аудите нет нового exact-SHA provider receipt; queued/in-progress не считается покрытием. |
| Central registry | `unverifiable`: `081de385…` не содержит результат PR #99; `222f2baf…` остаётся неслитым кандидатом. |
| Product runtime и public | `unverifiable`: новые discovery outputs не выпускались и не проверялись снаружи в рамках этого аудита. |

Полный машиночитаемый ledger с source revision, владельцами, hard gates и
release responsibility: [`cross-project-reuse-2026-08-28.json`](cross-project-reuse-2026-08-28.json).
