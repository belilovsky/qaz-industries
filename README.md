# QAZ.INDUSTRIES

QAZ.INDUSTRIES — самостоятельный статический продукт о проверяемых индустриях
Казахстана. Он связывает отраслевые показатели, цепочки, территориальный
контекст и ссылки на исходные публичные продукты, сохраняя период, источник и
границы каждого среза.

За 90 секунд:

- [Открыть публичный сайт](https://qaz.industries/).
- Перейти к четырём профилям: energy, space, farm и water через
  `industry.html?sector=...`.
- На [карте](https://qaz.industries/#map) доступны 20 проверенных региональных
  геометрий QazGeo; это территориальная основа, а не реестр объектов.
- На странице профиля можно сопоставить показатели, покрытие, источники,
  QazLake macro snapshot и QazGeo layer registry.
- [Бенчмарки](https://qaz.industries/benchmarks.html) фиксируют продуктовые слои,
  которые используются как исследовательские ориентиры.

Текущая source/runtime identity и доказательства выпуска находятся в
[`docs/current-release.md`](docs/current-release.md). Полный индекс документов —
в [`docs/index.md`](docs/index.md).

## Граница продукта

Браузер получает только reviewed static projections и локальные versioned assets.
QAZ.INDUSTRIES не публикует raw QazLake observations, private queues,
credentials, точные чувствительные координаты или неподтверждённые значения.
Региональные QazLake indicators и водный каталог сейчас показываются как
`degraded`; `contract_only` в QazGeo означает наличие описанного контракта без
наблюдаемого набора данных.

Манифест продукта — [`qazstack-thematic-product.json`](qazstack-thematic-product.json).
Наборы и их происхождение перечислены в [`docs/data-provenance.md`](docs/data-provenance.md).

## Поверхности и код

- `index.html` — входная страница, фильтр направлений и две карты QazGeo;
- `industry.html?sector=energy|space|farm|water` — профили и сравнение покрытия;
- `benchmarks.html` — семь международных референсов и матрица слоёв;
- `avds.css` — локальный consumer layer AV DS 4;
- `industry-data.js` — curated profile projection;
- `industry.js` — рендер профиля, snapshot modules и comparison;
- `qazgeo-map.js` — SVG-рендерер проверенного GeoJSON;
- `scripts/build_release.py` и `scripts/deploy.sh` — сборка и выпуск статического
  артефакта;
- `scripts/check.sh` — обязательный quality gate.

## Локальный запуск и проверки

Проект не требует установки пакетов для просмотра:

```bash
python3 -m http.server 8876 --bind 127.0.0.1
```

Откройте `http://127.0.0.1:8876/`. Перед изменением и перед review выполните:

```bash
scripts/check.sh
```

Проверки данных, маршрутов, JavaScript, Caddy-патчера и immutable release
описаны в [`docs/development-testing.md`](docs/development-testing.md).

## Выпуск

Порядок refresh, сборки, проверки runtime, rollback и public proof описан в
[`docs/operations.md`](docs/operations.md). Local green, runtime identity и
public/browser proof считаются разными видами доказательств. Commit, push и
deploy выполняются только владельцем выпуска.

Лицензия и окончательные правила attribution не угадываются автоматикой; см.
[`docs/security-privacy.md`](docs/security-privacy.md) и
[`docs/editorial-science-policy.md`](docs/editorial-science-policy.md).
