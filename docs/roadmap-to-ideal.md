# QAZ.INDUSTRIES — план доведения до идеального состояния

Документ предназначен для младших моделей и разработчиков. Каждый пункт
выполняется маленьким обратимым срезом: сначала доказательство состояния,
затем изменение, затем проверка.

Дата базовой фиксации: 2026-08-09.

## 1. Базовая точка

Канонический checkout:

~~~text
/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries
~~~

Репозиторий: https://github.com/belilovsky/qaz-industries.git

Последний проверенный commit: d833ef5fdcd024e80eca6b4e9cc2275bab231d21.

Последний публичный release: 20260809T103218Z-d833ef5fdcd0.

Публичные входы:

- https://qaz.industries/ — обзор и две карты QazGeo;
- https://qaz.industries/industry.html?sector=energy|space|farm|water — четыре профиля;
- https://qaz.industries/benchmarks.html — международные референсы;
- https://qaz.industries/api/health — runtime identity;
- https://qaz.industries/release.json — immutable release identity;
- https://qaz.industries/data/qazgeo-public-layer-registry.v1.json — reviewed metadata-only layer registry.

Уже закрыто:

- AV DS 4 tokens, components и patterns потребляются на всех трёх страницах;
- QazGeo-карта использует 20 реальных региональных геометрий, а не иллюстрацию;
- QazLake macro snapshot содержит три показателя с периодом, единицей,
  source URL и freshness gate;
- layer registry содержит шесть QazGeo-контрактов: четыре stable/observed и
  два contract_only для гидрологии и водных объектов;
- immutable release, Caddy patch fail-closed и host/container Caddy parity;
- local contract checks, route hygiene, JS syntax, unit tests, generated
  release artifact и public browser proof;
- robots.txt, sitemap.xml, canonical/OpenGraph metadata и ежедневный read-only
  public contract monitor.

Ограничения, которые нельзя маскировать:

1. Публичный QazLake endpoint региональных показателей и воды не предоставлен в
   текущей API-ревизии. Нельзя создавать значения из layer registry или
   заполнять пробел нулями.
2. contract_only означает «известен reviewed контракт», а не «данные загружены».
3. QazGeo OSM-слои требуют атрибуции и не являются инженерным, юридическим или
   оперативным реестром.
4. Resolver рабочего пространства пока не индексирует имя QAZ.INDUSTRIES. До
   исправления индекса канонический checkout определяется явным путём выше;
   соседние проекты менять нельзя.

## 2. Непереговорные правила

Перед каждой задачей:

1. Запиши проект, checkout, route/element, allowlist файлов и done-when.
2. Выполни git status --short --branch, git remote -v и git rev-parse HEAD.
3. Проверь, не изменён ли checkout пользователем. Не делай reset --hard, clean,
   prune, массовое удаление или rsync --delete.
4. Для данных установи provenance, период, единицу, freshness и license.
5. Для degraded/unknown используй явный empty state.
6. Не добавляй private QazLake, raw source fields, credentials, exact sensitive
   coordinates или непроверенные внешние значения.
7. После изменения запусти минимальную проверку; перед release — scripts/check.sh.
8. Local green, deployed green и public-browser green — три разные доказательства.

Минимальная цепочка доказательств:

~~~text
source -> tests -> immutable artifact -> runtime marker/health -> public HTTP -> browser
~~~

## 3. Шаблон задачи для младшей модели

~~~text
Цель: <одна проверяемая цель>
Checkout: /Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries
Файлы allowlist: <точные файлы>
Не трогать: соседние checkout, private data, Caddy вне QAZ-блока
Done when: <команды и наблюдаемые результаты>
Rollback: <git revert или переключение предыдущего release>
~~~

Шаблон отчёта:

~~~text
Изменено: <файлы>
Проверки: <точные команды и результат>
Commit: <sha>
Runtime: <release, health, header>
Public browser: <route, viewport, console, overflow>
Остаток/блокер: <одна строка или none>
~~~

Младшая модель не должна одновременно менять data schema, UI, Caddy и release
workflow. Разделяй работу на последовательные commit-срезы.

## 4. План по приоритетам

### P0 — обязательная гигиена каждого изменения

- чистый checkout перед deploy;
- scripts/check.sh;
- route/link hygiene;
- freshness и public policy gates;
- immutable release и runtime identity;
- desktop/mobile browser pass;
- no raw/private data gate.

Если P0 не проходит, следующие фазы не начинаются.

### P1 — интерфейс и доступность

1. Keyboard/ARIA audit: skip links, tab order, focus-visible, mobile menu,
   theme toggle, filters, sector switcher, compare selects и SVG map regions.
   Добавить smoke на activeElement, aria-expanded, aria-pressed и aria-live.
   Done: всё интерактивное работает Tab + Enter/Space, Escape закрывает меню,
   contrast не ухудшается в golden-paper.
2. Loading/error/empty matrix: 200, 404, malformed JSON, stale snapshot,
   offline для QazLake, QazGeo и layer registry. Не оставлять вечную загрузку.
   Done: Playwright route-mock smoke и console error = 0.
3. Responsive matrix: 320, 360, 390, 768, 1024 и 1440 px для всех страниц.
   Проверить таблицы, карты, source URL, CTA и reduced-motion.
   Done: scrollWidth не превышает innerWidth вне намеренно прокручиваемых таблиц.
4. Visual baseline: desktop/mobile screenshot в CI artifact, не в git. Сравнение
   делать только после human review.

### P2 — данные и provenance

1. Для каждого JSON требовать schema_version, status, retrieved_at, provider,
   publication_mode и limitations.
2. Разделять observed_snapshot, versioned_snapshot, contract_only и degraded.
3. Для refresh запускать три scripts/refresh_*.py в dry-run; сравнивать
   semantic diff без retrieved_at; только затем применять --write.
4. В каждой карточке показывать source, as-of, dataset status и limitation.
   OSM обязан показывать attribution, contract_only — upstream observation required.
5. Scheduled monitor должен завершаться failed при изменении layer IDs,
   public_allowed, projection, endpoint или license; он не коммитит и не
   деплоит.

### P3 — QazLake/QazGeo live integration

Фаза начинается только после upstream acceptance receipt: URL, owner,
auth/public policy, schema, sample response, rate limit, freshness, rollback и
license.

1. Regional indicators: shadow mode на одном регионе и одном metric ID, затем
   полный reviewed snapshot; missing values не превращать в ranking.
2. Water: отдельно catalogue (объекты/названия) и observations (уровень, дата,
   единица, sensor/source).
3. Browser получает только versioned public projection; raw/private QazLake
   остаётся server-side или закрытым.
4. Promotion: 30 дней стабильных probes, две проверки provenance/license,
   rollback test и browser degraded smoke.

Нельзя начинать эту фазу с угадывания endpoint.

### P4 — география и сценарии

1. Разрешать выбор слоя на карте только для observed_snapshot и
   versioned_snapshot.
2. Для инфраструктуры и транспорта использовать aggregate/viewport requests,
   а не скачивание полного набора в браузер.
3. Для каждого слоя показывать легенду, дату, attribution, coverage и limitation.
4. Добавлять permalink выбранного региона/слоя только после проверки точности.
5. На mobile держать touch target не менее 44px и уважать reduced-motion.

### P5 — качество продукта и контента

1. Для каждого профиля проверить одинаковый набор: title, summary, KPI,
   indicators, chain, geography, coverage, source links, gaps и compare.
2. Убрать формулировки «готово», если слой partial/degraded; не обещать live
   values там, где есть snapshot.
3. Зафиксировать русскую терминологию и vocabulary map для будущих kk/en версий.
4. Проверить уникальные title/description/OG, canonical, sitemap и robots через
   публичный HTTP.
5. Добавлять JSON-LD только для фактов с source/provenance; contract_only не
   размечать как наблюдаемый Dataset.

### P6 — runtime, security и performance

1. Проверять CSP, HSTS, nosniff, Referrer-Policy, frame policy,
   Permissions-Policy, COOP/CORP, no-store для health/release и Caddy parity.
2. Текущий CSP временно допускает unsafe-inline из-за inline bootstrap scripts
   и разрешает только Google Fonts hosts, используемые существующим import.
   Следующий срез должен self-host лицензированные woff2, вынести bootstrap в
   versioned JS или nonce и убрать unsafe-inline и внешнюю font dependency.
3. HTML/release identity — revalidate/no-store; versioned assets — immutable;
   data snapshots — короткий revalidate.
4. Зафиксировать HTML/CSS/JS/data budgets, Lighthouse mobile и long-task budget.
5. Провести rollback drill, stale Caddy bind-mount drill, malformed JSON, 404 и
   offline drill.

### P7 — юридическая и операционная готовность

1. Получить owner decision по лицензии QAZ-публикации и attribution wording.
2. Получить решения по QazLake/QazGeo data sharing и retention.
3. Добавить security contact только после подтверждения адреса.
4. Вести release ledger: source SHA, runtime release, probe timestamp, browser
   proof, rollback target и reviewer.
5. Не считать public domain доказательством прав на исходные данные.

## 5. Команды проверки

### Preflight

~~~bash
cd /Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries
git status --short --branch
git remote -v
git rev-parse HEAD
~~~

### Data dry-run

~~~bash
python3 scripts/refresh_qazlake_snapshot.py
python3 scripts/refresh_qazgeo_snapshot.py
python3 scripts/refresh_qazgeo_layer_registry.py
~~~

### Полный quality gate

~~~bash
scripts/check.sh
~~~

Ожидаемый минимум:

~~~text
static contract: OK
route hygiene: OK
public contract: OK
OK (unit tests)
data contract: OK
release artifact contract: OK
~~~

### Browser proof

Одна сессия Browser/Playwright, после проверки закрыть:

- desktop 1440×1200: home, industry sector=farm, benchmarks;
- mobile 390×844: home, industry sector=water, benchmarks;
- release identity через release.json;
- map paths = 40, layer cards = 6, contract_only = 2;
- console error = 0;
- scrollWidth <= innerWidth;
- mobile menu, theme, sector switcher, map zoom/selection и compare.

### Release proof

~~~bash
git diff --check
git status --short
scripts/deploy.sh
curl -fsS https://qaz.industries/api/health
curl -fsSI https://qaz.industries/
curl -fsS https://qaz.industries/release.json
curl -fsS https://qaz.industries/robots.txt
curl -fsS https://qaz.industries/sitemap.xml
~~~

На VPS дополнительно:

~~~bash
readlink /opt/qdev-public-sites/www/qaz.industries/current
sha256sum /opt/qdev-public-sites/Caddyfile
docker exec qdev-public-sites-proxy sha256sum /etc/caddy/Caddyfile
~~~

## 6. Что можно закрыть самостоятельно, а что является блокером

Можно закрыть самостоятельно: tests, route hygiene, metadata, discovery files,
empty states, responsive/accessibility fixes, immutable release checks, docs,
CI probes и verified metadata-only registry.

Нельзя закрывать догадкой: отсутствующий QazLake endpoint, неизвестную лицензию,
private/authenticated data, точность OSM geometry, owner decision по retention,
attribution или public sharing.

В блокере результатом должны быть fail-closed UI, receipt-запрос и точная
строка в ledger.

## 7. Definition of Ideal

QAZ.INDUSTRIES идеален, когда одновременно выполнены все условия:

- каждый публичный факт имеет source, период, единицу, status и limitation;
- каждая страница проходит keyboard, screen-reader, responsive, reduced-motion и
  visual QA;
- upstream outage виден пользователю и не создаёт ложных нулей;
- release воспроизводим из commit, immutable и откатываем;
- public HTTP, runtime identity, Caddy parity и browser proof совпадают;
- CI ежедневно проверяет contracts, но не публикует изменения без review;
- license, attribution, retention и owner approvals документированы;
- junior model может выполнить задачу по шаблону, не угадывая архитектуру и не
  затрагивая чужие проекты.
