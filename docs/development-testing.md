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

Она выполняет static HTML/AV DS contract, route hygiene, accessibility и
терминологический contracts, size/security budgets, public data contracts,
documentation links, Python compile checks, 8 Python unit tests, data contract, 9 Node tests,
синтаксис всех JavaScript и shell scripts, build release во временной директории,
release artifact verification и `git diff --check`.

Отдельные полезные команды:

```bash
python3 scripts/check_static_site.py
python3 scripts/check_routes.py
python3 scripts/check_accessibility.py
python3 scripts/check_content.py
python3 scripts/check_quality_budgets.py
python3 scripts/check_docs.py
python3 scripts/check_public_contracts.py
python3 scripts/check_sector_sources.py
node scripts/check_data_contract.mjs
node --test tests/*.test.cjs
python3 -m unittest discover -s tests -v
```

Refresh scripts без `--write` дают read-only probe; `--write` требует review
каждого diff. Общий `scripts/public_snapshot.py` проверяет HTTPS, UTC timestamp
и выполняет staged atomic writes. Проверка freshness — максимум 31 день.

## CI и monitor

`.github/workflows/ci.yml` запускает `scripts/check.sh` на push в `main` и pull
request. `.github/workflows/public-contract-monitor.yml` запускается ежедневно
в `03:17 UTC` и вручную; он пишет probe output в `/tmp`, загружает artifact на 7
дней и не коммитит snapshots и не деплоит.

## Browser proof

После UI-изменения требуется одна закрытая browser session: desktop и 390px,
все четыре страницы, четыре sector states, theme/menu/filter/compare/map
interactions, console errors, scroll width, source links и release identity.
Старый screenshot или строка в roadmap не заменяют текущий proof.

## Ограничения проверки

Автоматический gate не проверяет полную редакционную корректность upstream,
лицензию, рынок, staging или реальную доступность каждого внешнего source URL.
Эти факты должны иметь отдельное evidence и owner decision.
