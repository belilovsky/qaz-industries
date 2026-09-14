# QAZ.INDUSTRIES — contract for agents

Канонический продукт: QAZ.INDUSTRIES, checkout `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries`, публичная поверхность — `https://qaz.industries/`.

Перед изменением прочитайте [`docs/index.md`](docs/index.md) и [`docs/current-release.md`](docs/current-release.md). Для правил данных и публикации используйте [`docs/data-provenance.md`](docs/data-provenance.md), для выпуска — [`docs/operations.md`](docs/operations.md).

Граница продукта: статический публичный сайт и reviewed snapshots. Не добавляйте в браузер прямой доступ к QazLake/QazGeo, raw/private данные, точные чувствительные координаты, credentials или неподтверждённые числа. Contract-only слой не является наблюдением.

Перед изменением сохраните `git status --short --branch`, remote и `git rev-parse HEAD`. Минимальная проверка: `scripts/check.sh`; локальный результат не заменяет runtime и public proof. Не меняйте общий Caddyfile вне блока QAZ.INDUSTRIES. Не выполняйте commit, push или deploy без отдельного разрешения.

<!-- qdev-runner-policy:start -->
## QDev GitHub Actions runner policy

- General CI must use the centralized ephemeral self-hosted pool. Select one
  approved profile (`qdev-ci`, `qdev-ci-browser`, or `qdev-ci-docker`) together
  with `self-hosted`, `Linux`, `X64`, and a job-unique `qdev-job-*` label.
- Treat `.github/qdev-runner.yml` as the machine-readable source of truth. Do
  not create a repository-specific runner or add a GitHub-hosted fallback.
- Pin third-party actions to a full 40-character commit SHA. Do not make
  `actions/cache`, GitHub Artifacts, GitHub Packages, or GHCR an availability
  dependency; use the QDev artifact and registry services documented in
  `.github/QDEV_RUNNERS.md`.
- Public fork pull requests must not execute fork code on production-connected
  runners. Keep product-specific deployment labels and their credential gates
  separate from the general CI pool.
- Any new or changed workflow must pass the `qdev-runner-contract` check.
<!-- qdev-runner-policy:end -->
