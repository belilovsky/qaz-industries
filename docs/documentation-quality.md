# Качество документации

## Правило одного текущего статуса

Текущая source/runtime/public identity хранится только в
[`current-release.md`](current-release.md). README и исторические документы
ссылаются на него, не создавая вторую дату или release ID.

## Перед review

- `git status --short --branch`, remote и `git rev-parse HEAD` подтверждают
  checkout;
- ссылки Markdown ведут к существующим файлам или явно помечены external;
- домен, название QAZ.INDUSTRIES и route set не расходятся;
- числа имеют источник, дату, единицу и описание методики;
- source-confirmed, local-tested, runtime-verified и public-verified не смешаны;
- historical/planned/proposed/blocked/unknown обозначены явно;
- нет маркеров незавершённости, credentials, PII и старых release claims без historical label;
- команды в документации существуют и не требуют скрытых секретов;
- документация не обещает модули, API или production integrations, которых нет.

## Лингвистическая гигиена

Используйте прямой профессиональный русский язык. Удаляйте рекламные клише,
пустые вступления и неопределённые превосходные степени. Технический термин
оставляйте только как официальный contract/name или когда русский эквивалент
теряет точность.

## Evidence layers

`source-confirmed` → `local-tested` → generated artifact → runtime marker/health
→ public HTTP → browser proof. Ни один слой не заменяет следующий.

## История

Исторические планы не удаляются, но их дата и статус должны быть видны, а
текущие факты должны ссылаться на `current-release.md`. Ignored `work/` ledgers
не являются durable documentation source.
