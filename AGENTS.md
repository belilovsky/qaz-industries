# QAZ.INDUSTRIES — contract for agents

Канонический продукт: QAZ.INDUSTRIES, checkout `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries`, публичная поверхность — `https://qaz.industries/`.

Перед изменением прочитайте [`docs/index.md`](docs/index.md) и [`docs/current-release.md`](docs/current-release.md). Для правил данных и публикации используйте [`docs/data-provenance.md`](docs/data-provenance.md), для выпуска — [`docs/operations.md`](docs/operations.md).

Граница продукта: статический публичный сайт и reviewed snapshots. Не добавляйте в браузер прямой доступ к QazLake/QazGeo, raw/private данные, точные чувствительные координаты, credentials или неподтверждённые числа. Contract-only слой не является наблюдением.

Перед изменением сохраните `git status --short --branch`, remote и `git rev-parse HEAD`. Минимальная проверка: `scripts/check.sh`; локальный результат не заменяет runtime и public proof. Не меняйте общий Caddyfile вне блока QAZ.INDUSTRIES. Не выполняйте commit, push или deploy без отдельного разрешения.
