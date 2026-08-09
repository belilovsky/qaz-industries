# Текущий статус выпуска

Дата проверки: **2026-08-09**. Это единственный документ, в котором описывается
текущий source/runtime/public status; исторические планы не переопределяют его.

## Identity

| Поле | Значение | Достоверность |
|---|---|---|
| Project | QAZ.INDUSTRIES | source-confirmed |
| Checkout | `/Users/belilovsky/Documents/Codex/2026-08-09/qaz-industries` | source-confirmed |
| Remote | `https://github.com/belilovsky/qaz-industries.git` | source-confirmed |
| Branch | `main` | source-confirmed |
| Source SHA | `12f27b3396594e4a05bc2a5039b6b601fe736245` | source-confirmed |
| Public domain | `https://qaz.industries/` | public-verified |
| Runtime owner | shared public-sites Caddy | source-confirmed; exact operator unknown |
| Public release | `20260809T111221Z-12f27b339659` | public-verified |

После этой documentation-only write-фазы checkout содержит только изменения
документации и не был committed или deployed. `12f27b339659…` — commit
последнего public release; новые документы находятся в dirty working tree и не
предъявляются как production release.

## Evidence

- `scripts/check.sh`: `static contract: OK`, `route hygiene: OK`, `public
  contract: OK`, 3 unit tests `OK`, `data contract: OK (4 profiles)`, `release
  artifact contract: OK` — local-tested.
- `https://qaz.industries/api/health` returns `status=ok`, service
  `qaz-industries`, the release above — public-verified.
- `https://qaz.industries/release.json` returns the same release and source SHA —
  public-verified.
- Root, profile routes, benchmarks, data contracts and listed assets returned
  HTTP 200 during the 2026-08-09 public probe — public-verified.
- Current browser proof was not rerun in this documentation pass; previous
  browser claims remain historical until a new receipt is attached.

## Upstream public checks

Эти наблюдения сделаны через публичные страницы 2026-08-09 и не импортированы в
checkout автоматически:

- [Qazaqstan.Space](https://qazaqstan.space/) показывает выпуск `2026-08-06.48`;
- [QAZ.FARM](https://qaz.farm/) показывает дату выпуска `2026-08-09` и 101
  источник;
- [QAZ.FISH](https://qaz.fish/) содержит public structured-data updates
  `2026-08-09T10:21:00Z`, `13:45:00+05:00` и `16:27:37+05:00`;
- [QZ.Energy](https://qz.energy/) показывает 157 показателей и 18 объектов.

Это public-verified evidence доступности upstream, но не owner receipt на
перенос release labels в curated projection. Локальные labels остаются
историческими до отдельного review.

## Source versus generated release

Tracked source data can use `release_id: "source"`. `scripts/build_release.py`
replaces it in the generated artifact with the immutable release ID. The public
thematic release currently carries `20260809T111221Z-12f27b339659`; this distinction
must be preserved when comparing checkout JSON with runtime JSON.

## Rollback and staging

`scripts/deploy.sh` creates an immutable release, validates the QAZ Caddy block,
checks parity and can restore the previous symlink/configuration. No staging URL
or staging receipt is present in this checkout. VPS path/digest evidence is not
claimed from a local workstation.

## Open blockers

- `qazstack-consumer.json` is referenced by the manifest but absent locally.
- Profile release labels need owner-confirmed refresh against current upstream
  pages.
- Regional QazLake indicators and water catalogue remain degraded.
- QAZ publication licence, attribution, retention and security contact need
  owner decisions.
