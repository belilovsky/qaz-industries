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
- `industry-data.js` — изолированный локальный data layer, готовый к замене API.

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

`scripts/build-release.py` собирает неизменяемый static artifact в `.build/`.
`scripts/deploy.sh` публикует его в отдельную директорию release, проверяет
Caddy и только затем переключает `current` symlink. Скрипт не меняет HAProxy:
домен уже находится в его публичном маршруте.

Перед публикацией обязательны source checks, runtime marker, `/api/health`,
ключевые assets и browser proof. Полный порядок описан в
[`docs/operations.md`](docs/operations.md).
