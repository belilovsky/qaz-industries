# Индекс документации

Этот индекс — навигация по текущей документации QAZ.INDUSTRIES. Дата проверки
этой редакции: 2026-08-09. Источник факта выбирается в следующем порядке:

1. исходный код, manifest и public data contracts;
2. текущий release receipt и runtime/public evidence;
3. эксплуатационные инструкции;
4. исторические планы и отчёты.

Метки достоверности: `source-confirmed`, `local-tested`, `runtime-verified`,
`public-verified`, `historical`, `planned`, `proposed`, `blocked`, `unknown`.

| Документ | Назначение | Аудитория | Статус | Владелец факта |
|---|---|---|---|---|
| [`README.md`](../README.md) | 90-секундный обзор и быстрый запуск | все | active | manifest, source, current release |
| [`AGENTS.md`](../AGENTS.md) | короткий contract для агентов | разработчики и ИИ | active | project boundary |
| [`product-overview.md`](product-overview.md) | миссия, пользователи, сценарии и non-goals | все | active | product owner |
| [`architecture.md`](architecture.md) | границы системы и потоки данных | разработчики, аудиторы | active | source, Caddy fragment |
| [`modules.md`](modules.md) | каталог шести модулей и их fail-closed правил | разработчики | active | manifest, JS, data contracts |
| [`interfaces.md`](interfaces.md) | маршруты, runtime endpoints и browser interactions | разработчики, интеграторы | active | HTML, JS, Caddy |
| [`data-provenance.md`](data-provenance.md) | datasets, lineage, freshness и ограничения | специалисты по данным, редакторы, аудиторы | active | JSON contracts, source registry |
| [`portfolio-integrations.md`](portfolio-integrations.md) | направление и статус связей с портфелем | владельцы продуктов | active | source registry, manifest |
| [`security-privacy.md`](security-privacy.md) | классы данных, запреты и правовые решения | все, security | active | manifest, Caddy, SECURITY.md |
| [`editorial-science-policy.md`](editorial-science-policy.md) | включение, проверка и исправление материалов | редакция, исследователи | active | source policy, owner decisions |
| [`design-language-accessibility.md`](design-language-accessibility.md) | AV DS 4, русский язык и accessibility contract | frontend, редакция | active | avds.css, HTML, JS |
| [`development-testing.md`](development-testing.md) | локальная работа и quality gates | разработчики | active | scripts, workflows |
| [`operations.md`](operations.md) | выпуск, runtime verification и rollback | эксплуатация | active | deploy script, Caddy fragment |
| [`current-release.md`](current-release.md) | единственный текущий release status | все | active | runtime/public probes |
| [`observability.md`](observability.md) | health, release identity, monitor и диагностика | эксплуатация | active | Caddy, workflows |
| [`risks-and-technical-debt.md`](risks-and-technical-debt.md) | ограничения и решения владельца | владельцы, разработчики | active | current source and evidence |
| [`investor-critic-brief.md`](investor-critic-brief.md) | честный brief без выдуманных metrics | инвесторы, критики | active | confirmed evidence only |
| [`ai-context.md`](ai-context.md) | подробный контекст для продолжения работы | ИИ-агенты | active | all active docs |
| [`documentation-quality.md`](documentation-quality.md) | правила актуальности и link audit | maintainers, аудиторы | active | docs inventory and checks |
| [`completion-ledger.md`](completion-ledger.md) | результат documentation audit и остаточные блокеры | владельцы задачи | review_pending | this documentation pass |
| [`roadmap-to-ideal.md`](roadmap-to-ideal.md) | исторический план для младших моделей | разработчики | historical/plan | archived plan; current-release supersedes identity |

`SECURITY.md` и `CONTRIBUTING.md` остаются короткими entrypoints; подробные
правила находятся в документах выше. Внешние проекты в этом checkout не
являются локальными модулями и не должны описываться как production
integrations без отдельного evidence.
