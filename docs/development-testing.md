# Разработка и проверки

## Локальный запуск

Проект — static site без обязательной установки пакетов:

```bash
python3 -m http.server 8876 --bind 127.0.0.1
```

Откройте `http://127.0.0.1:8876/`. Перед изменением сохраните состояние Git и
проверьте, что checkout соответствует [`current-release.md`](current-release.md).

## Quality gate

Единая команда:

```bash
scripts/check.sh
```

Она выполняет static HTML/AV DS contract, route hygiene, public data contracts,
Python compile checks, unit tests Caddy-патчера, data contract, JavaScript syntax,
build release в temporary directory, release artifact verification и `git diff
--check`.

Отдельные полезные команды:

```bash
python3 scripts/check_static_site.py
python3 scripts/check_routes.py
python3 scripts/check_public_contracts.py
node scripts/check_data_contract.mjs
python3 -m unittest discover -s tests -v
```

Refresh scripts без `--write` дают read-only probe; `--write` требует review
каждого diff. Проверка freshness — максимум 31 день.

## CI и monitor

`.github/workflows/ci.yml` запускает `scripts/check.sh` на push в `main` и pull
request. `.github/workflows/public-contract-monitor.yml` запускается ежедневно
в `03:17 UTC` и вручную; он пишет probe output в `/tmp`, загружает artifact на 7
дней и не коммитит snapshots и не деплоит.

## Browser proof

После UI-изменения требуется одна закрытая browser session: desktop и 390px,
все три страницы, четыре sector states, theme/menu/filter/compare/map
interactions, console errors, scroll width, source links и release identity.
Старый screenshot или строка в roadmap не заменяют текущий proof.

## Ограничения проверки

Автоматический gate не проверяет полную редакционную корректность upstream,
лицензию, рынок, staging или реальную доступность каждого внешнего source URL.
Эти факты должны иметь отдельное evidence и owner decision.
