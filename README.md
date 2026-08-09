# QAZ.INDUSTRIES

Канонический статический сайт об индустриях Казахстана: отраслевые профили,
показатели, объекты, география, контекст и проверяемые источники.

Это самостоятельный продукт, а не output другого портфельного проекта.

## Поверхности

- `index.html` — точка входа и карта экосистемы;
- `industry.html?sector=energy|space|farm|water` — профили отраслей и сравнение покрытия;
- `benchmarks.html` — семь международных референсов и восемь обязательных слоёв продукта;
- `avds.css` — локальный AV DS 4 compatibility layer: токены, semantic states,
  focus, motion и responsive control sizes;
- `industry-data.js` — изолированный локальный data layer, готовый к замене API;
- `scripts/patch_caddy_release.py` — fail-closed патчер, который может менять
  только собственный блок домена в общем Caddyfile.

## Данные и публичные контракты

`qazstack-thematic-product.json` фиксирует product boundary: QAZ публикует
только reviewed static projections, а не raw QazLake, private queues или
прямой browser access к lake. В `data/` доступны профильный JSON, reviewed
source registry, тематический release и публичный macro snapshot QazLake.

Обновление snapshot является явным review-step: сначала проверить diff, затем
только при необходимости записать новый файл.

```bash
python3 scripts/refresh_qazlake_snapshot.py
python3 scripts/refresh_qazlake_snapshot.py --write
scripts/check.sh
```

Проверка не пропустит релиз со snapshot старше 31 дня. Недоступные public API
слои QazLake показываются пользователю как degraded, а не маскируются пустыми
карточками.

Числа не синтетические: каждый показатель сопровождается периодом, контекстом
и ссылкой на публичный источник. Отсутствующее покрытие показывается как
пробел, а не как нулевое значение.

## Локальная работа

```bash
python3 -m http.server 8876 --bind 127.0.0.1
```

Откройте `http://127.0.0.1:8876/`. Перед коммитом выполните:

```bash
scripts/check.sh
```

## Релизы

`scripts/build_release.py` собирает неизменяемый static artifact в `.build/`.
`scripts/deploy.sh` публикует его в отдельную директорию release, проверяет
Caddy до переключения `current` symlink. Скрипт не меняет HAProxy:
домен уже находится в его публичном маршруте.

Перед публикацией обязательны source checks, runtime marker, `/api/health`,
ключевые assets и browser proof. Полный порядок описан в
[`docs/operations.md`](docs/operations.md).

## Качество и границы

CI запускает тот же `scripts/check.sh`, что и локальная работа: структурный
контракт страниц, schema/provenance data layer, unit-тест изолированного Caddy
патчера, JavaScript syntax и проверку immutable release artifact. Динамический
рендеринг экранирует текст и принимает только HTTPS-ссылки и известные states.

Лицензия намеренно не предполагается: юридический режим публикации должен быть
выбран владельцем отдельно, а не угадан автоматизацией.
