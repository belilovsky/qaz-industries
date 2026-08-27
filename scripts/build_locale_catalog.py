#!/usr/bin/env python3
"""Build and verify the local RU/KK/EN interface translation catalog.

The public site never calls a third-party translation service.  ``--write`` is
an operator-only refresh command; the generated catalog is shipped as a
same-origin release asset and ``--check`` verifies that source strings have not
outgrown it.
"""

from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import time
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "ui-locale.v1.json"
SPLIT = "__QAZ_I18N_SPLIT__"
CYRILLIC = re.compile(r"[А-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүҺһІі]")
JS_STRING = re.compile(r"(['\"`])((?:\\.|(?!\1).)*?)\1", re.DOTALL)
TEMPLATE_EXPR = re.compile(r"\$\{[^{}]*\}")
AVDS_BADGE_LABEL = re.compile(
    r"^Общее покрытие AVDS (?P<version>4\.\d+\.\d+): (?P<coverage>\d+) процентов; "
    r"базовый маршрутный контракт: (?P<routes>\d+) процент(?:а|ов)?$"
)
TARGETS = {"kk-KZ": "kk", "en-US": "en"}
MANUAL_OVERRIDES = {
    "kk-KZ": {
        "Пробел": "Бос орын",
        "Выпуски": "Шығарылымдар",
        "Значение": "Мәні",
        "Реестр": "Тізілім",
        "Обзор": "Шолу",
        "Выгрузка": "Экспорт",
        "Срез": "Деректер кесіндісі",
        "Практика": "Практика",
        "Тема": "Тақырып",
        "Показано": "Көрсетілді",
        "процент": "пайыз",
        "процента": "пайыз",
        "процентов": "пайыз",
        "; базовый маршрутный контракт:": "; негізгі маршруттық келісімшарт:",
        "Выпуск qz-energy-newsroom-4100f6a1-20260826 · данные на 6 августа": "qz-energy-newsroom-4100f6a1-20260826 шығарылымы · 6 тамыздағы деректер",
        "Контракт принятия QazStack": "QazStack қабылдау келісімшарты",
        "Манифест Platform": "Platform манифесі",
        "Продуктовый контракт QazStack": "QazStack өнімдік келісімшарты",
        "25 августа 2026": "2026 жылғы 25 тамыз",
        "Выпуск 2026-08-21.1 · данные на 24 августа": "2026-08-21.1 шығарылымы · 24 тамыздағы деректер",
        "Выпуск 2026-08-25.2 · данные на 25 августа": "2026-08-25.2 шығарылымы · 25 тамыздағы деректер",
        "Выпуск qazgeo-20260825T102556931z · данные на 25 августа": "qazgeo-20260825T102556931z шығарылымы · 25 тамыздағы деректер",
        "выпуск 2026-08-25.2": "2026-08-25.2 шығарылымы",
        "проверенных фактов": "тексерілген факт",
        "фактов": "факт",
        "Берег озера Белое в Шортандинском районе Акмолинской области: удочка у воды и степной горизонт.": "Ақмола облысы Шортанды ауданындағы Белое көлінің жағалауы: су жанындағы қармақ пен дала көкжиегі.",
        "Ветровые турбины Кордайской ВЭС на юго-востоке Казахстана.": "Қазақстанның оңтүстік-шығысындағы Қордай жел электр станциясының жел турбиналары.",
        "Корабль Soyuz TMA-09M на стартовой площадке Байконура. Документальный контекст, не оперативный статус программы.": "Байқоңырдың ұшыру алаңындағы Soyuz TMA-09M кемесі. Құжаттық контекст, бағдарламаның жедел мәртебесі емес.",
        "Корабль Soyuz TMA-09M на стартовой площадке космодрома Байконур.": "Байқоңыр ғарыш айлағының ұшыру алаңындағы Soyuz TMA-09M кемесі.",
        "Кордайская ВЭС на юго-востоке Казахстана. Документальный контекст; кадр не является сводкой текущего состояния объекта.": "Қазақстанның оңтүстік-шығысындағы Қордай жел электр станциясы. Құжаттық контекст; кадр объектінің қазіргі жай-күйінің жиынтығы емес.",
        "МаратД": "МаратД",
        "Озеро Белое, Шортандинский район, Акмолинская область. Документальный контекст для темы водоёмов и рыболовства.": "Белое көлі, Шортанды ауданы, Ақмола облысы. Су айдындары мен балық аулау тақырыбына арналған құжаттық контекст.",
        "Спутниковый снимок NASA: сезонная структура сельскохозяйственных участков в Казахстане. Это документальный контекст дистанционного зондирования, не текущая статистика.": "NASA спутниктік суреті: Қазақстандағы ауылшаруашылық алқаптарының маусымдық құрылымы. Бұл қашықтан зондтаудың құжаттық контексті, қазіргі статистика емес.",
        "Спутниковый снимок сельскохозяйственных участков и долин в Казахстане.": "Қазақстандағы ауылшаруашылық алқаптары мен аңғарларының спутниктік суреті.",
        "Фото:": "Фото:",
    },
    "en-US": {
        "Пробел": "Gap",
        "Выпуски": "Releases",
        "Значение": "Value",
        "Реестр": "Registry",
        "Обзор": "Overview",
        "Выгрузка": "Export",
        "Срез": "Snapshot",
        "Практика": "Practice",
        "Тема": "Theme",
        "Показано": "Shown",
        "процент": "percent",
        "процента": "percent",
        "процентов": "percent",
        "; базовый маршрутный контракт:": "; baseline route contract:",
        "Выпуск qz-energy-newsroom-4100f6a1-20260826 · данные на 6 августа": "Release qz-energy-newsroom-4100f6a1-20260826 · data as of August 6",
        "Контракт принятия QazStack": "QazStack acceptance contract",
        "Манифест Platform": "Platform manifest",
        "Продуктовый контракт QazStack": "QazStack product contract",
        "25 августа 2026": "August 25, 2026",
        "Выпуск 2026-08-21.1 · данные на 24 августа": "Release 2026-08-21.1 · data as of August 24",
        "Выпуск 2026-08-25.2 · данные на 25 августа": "Release 2026-08-25.2 · data as of August 25",
        "Выпуск qazgeo-20260825T102556931z · данные на 25 августа": "Release qazgeo-20260825T102556931z · data as of August 25",
        "выпуск 2026-08-25.2": "release 2026-08-25.2",
        "проверенных фактов": "verified facts",
        "фактов": "facts",
        "Берег озера Белое в Шортандинском районе Акмолинской области: удочка у воды и степной горизонт.": "The shore of Lake Beloye in the Shortandy District of Akmola Region: a fishing rod by the water and the steppe horizon.",
        "Ветровые турбины Кордайской ВЭС на юго-востоке Казахстана.": "Wind turbines at the Korday wind farm in southeastern Kazakhstan.",
        "Корабль Soyuz TMA-09M на стартовой площадке Байконура. Документальный контекст, не оперативный статус программы.": "The Soyuz TMA-09M spacecraft on the Baikonur launch pad. Documentary context, not the programme's operational status.",
        "Корабль Soyuz TMA-09M на стартовой площадке космодрома Байконур.": "The Soyuz TMA-09M spacecraft on the Baikonur Cosmodrome launch pad.",
        "Кордайская ВЭС на юго-востоке Казахстана. Документальный контекст; кадр не является сводкой текущего состояния объекта.": "The Korday wind farm in southeastern Kazakhstan. Documentary context; this image is not a summary of the facility's current status.",
        "МаратД": "МаратД",
        "Озеро Белое, Шортандинский район, Акмолинская область. Документальный контекст для темы водоёмов и рыболовства.": "Lake Beloye, Shortandy District, Akmola Region. Documentary context for the water bodies and fishing theme.",
        "Спутниковый снимок NASA: сезонная структура сельскохозяйственных участков в Казахстане. Это документальный контекст дистанционного зондирования, не текущая статистика.": "NASA satellite imagery: the seasonal structure of agricultural fields in Kazakhstan. This is documentary remote-sensing context, not current statistics.",
        "Спутниковый снимок сельскохозяйственных участков и долин в Казахстане.": "A satellite image of agricultural fields and valleys in Kazakhstan.",
        "Фото:": "Photo:",
    },
}
HTML_PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
JS_FILES = (
    "locale.js",
    "site-shell.js",
    "app.js",
    "qazgeo-map.js",
    "profile-view.js",
    "industry-data.js",
    "industry.js",
)


def normalize(value: str) -> str:
    return " ".join(str(value).split()).strip()


def is_copy(value: str) -> bool:
    value = normalize(value)
    if len(value) < 2 or not CYRILLIC.search(value):
        return False
    if any(marker in value for marker in ("${", "=>", "locale.", "escapeHtml", "provider.", "snapshot.", "state ===", "data/")):
        return False
    return True


class CopyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.values: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip += 1
        for name, value in attrs:
            if value and name in {"aria-label", "title", "alt", "placeholder", "content"}:
                if is_copy(value):
                    self.values.add(normalize(value))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip and is_copy(data):
            self.values.add(normalize(data))


def add_json_values(value: object, output: set[str]) -> None:
    if isinstance(value, str):
        if is_copy(value):
            output.add(normalize(value))
    elif isinstance(value, dict):
        for item in value.values():
            add_json_values(item, output)
    elif isinstance(value, list):
        for item in value:
            add_json_values(item, output)


def add_js_strings(source: str, output: set[str]) -> None:
    for match in JS_STRING.finditer(source):
        quote, body = match.groups()
        if quote == "`":
            value = body
        else:
            try:
                value = ast.literal_eval(match.group(0))
            except (SyntaxError, ValueError):
                value = body
        value = TEMPLATE_EXPR.sub(" ", value)
        for fragment in re.split(r"\s{2,}|[<>]", value):
            if is_copy(fragment):
                output.add(normalize(fragment))


def source_inventory() -> list[str]:
    values: set[str] = set()
    for filename in HTML_PAGES:
        parser = CopyParser()
        parser.feed((ROOT / filename).read_text(encoding="utf-8"))
        parser.close()
        values.update(parser.values)
    for filename in JS_FILES:
        add_js_strings((ROOT / filename).read_text(encoding="utf-8"), values)
    for directory in (ROOT / "content", ROOT / "data"):
        for path in sorted(directory.glob("*.json")):
            if path == CATALOG:
                continue
            try:
                add_json_values(json.loads(path.read_text(encoding="utf-8")), values)
            except json.JSONDecodeError:
                continue
    return sorted(values)


def inventory_hash(values: Iterable[str]) -> str:
    payload = "\n".join(values).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def translate_batch(values: list[str], target: str) -> dict[str, str]:
    joined = f"\n{SPLIT}\n".join(values)
    query = urlencode({"client": "gtx", "sl": "ru", "tl": target, "dt": "t", "q": joined})
    request = Request(
        f"https://translate.googleapis.com/translate_a/single?{query}",
        headers={"User-Agent": "qaz-industries-locale-builder/1.0"},
    )
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    translated = "".join(part[0] for part in (payload[0] or []) if part and part[0])
    pieces = [normalize(item) for item in translated.split(SPLIT)]
    if len(pieces) != len(values):
        raise RuntimeError(f"translation segment mismatch for {target}: {len(values)} -> {len(pieces)}")
    return dict(zip(values, pieces))


def batches(values: list[str], max_chars: int = 1600) -> list[list[str]]:
    result: list[list[str]] = []
    current: list[str] = []
    size = 0
    for value in values:
        addition = len(value) + len(SPLIT) + 2
        if current and size + addition > max_chars:
            result.append(current)
            current = []
            size = 0
        current.append(value)
        size += addition
    if current:
        result.append(current)
    return result


def derived_translation(value: str, locale: str) -> str | None:
    """Translate stable numeric AVDS receipt labels without network access."""
    match = AVDS_BADGE_LABEL.fullmatch(value)
    if not match:
        return None
    fields = match.groupdict()
    if locale == "kk-KZ":
        return (
            f"AVDS {fields['version']} жалпы қамтуы: {fields['coverage']} пайыз; "
            f"негізгі маршруттық келісімшарт: {fields['routes']} пайыз"
        )
    if locale == "en-US":
        return (
            f"AVDS {fields['version']} overall coverage: {fields['coverage']} percent; "
            f"baseline route contract: {fields['routes']} percent"
        )
    return None


def write_catalog() -> None:
    values = source_inventory()
    if not values:
        raise SystemExit("locale catalog: source inventory is empty")
    previous: dict[str, dict[str, str]] = {}
    if CATALOG.is_file():
        try:
            existing = json.loads(CATALOG.read_text(encoding="utf-8"))
            translations = existing.get("translations") or {}
            previous = {
                locale: mapping
                for locale, mapping in translations.items()
                if isinstance(mapping, dict)
            }
        except (OSError, json.JSONDecodeError):
            previous = {}
    translated: dict[str, dict[str, str]] = {"ru-RU": {value: value for value in values}}
    for locale, target in TARGETS.items():
        locale_values = {
            value: previous.get(locale, {}).get(value, "")
            for value in values
            if isinstance(previous.get(locale, {}).get(value), str) and previous[locale][value].strip()
        }
        locale_values.update({
            key: value
            for key, value in MANUAL_OVERRIDES.get(locale, {}).items()
            if key in values and key not in locale_values
        })
        for value in values:
            if value not in locale_values:
                translated_value = derived_translation(value, locale)
                if translated_value:
                    locale_values[value] = translated_value
        missing = [value for value in values if value not in locale_values]
        if missing:
            work = batches(missing)
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(translate_batch, batch, target): batch for batch in work}
                for future in as_completed(futures):
                    locale_values.update(future.result())
        locale_values.update({key: value for key, value in MANUAL_OVERRIDES.get(locale, {}).items() if key in locale_values})
        if set(locale_values) != set(values) or any(not value for value in locale_values.values()):
            raise SystemExit(f"locale catalog: incomplete {locale}")
        translated[locale] = dict(sorted(locale_values.items()))
    catalog = {
        "schema_version": "qaz-industries-ui-locale-v1",
        "product_id": "qaz-industries",
        "source_locale": "ru-RU",
        "supported_locales": ["ru-RU", "kk-KZ", "en-US"],
        "inventory": {"source_count": len(values), "source_sha256": inventory_hash(values)},
        "policy": "Interface and public source metadata are translated locally; proper names, URLs, units and source identifiers stay stable.",
        "translations": translated,
    }
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"locale catalog: wrote {len(values)} source strings")


def check_catalog() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    values = source_inventory()
    require = lambda condition, message: (_ for _ in ()).throw(ValueError(message)) if not condition else None
    require(catalog.get("schema_version") == "qaz-industries-ui-locale-v1", "schema")
    require(catalog.get("source_locale") == "ru-RU", "source locale")
    require(catalog.get("supported_locales") == ["ru-RU", "kk-KZ", "en-US"], "locale matrix")
    inventory = catalog.get("inventory") or {}
    require(inventory.get("source_count") == len(values), "source count drift")
    require(inventory.get("source_sha256") == inventory_hash(values), "source inventory drift")
    translations = catalog.get("translations") or {}
    for locale in ("ru-RU", "kk-KZ", "en-US"):
        mapping = translations.get(locale) or {}
        require(set(mapping) == set(values), f"{locale} translation coverage")
        require(all(isinstance(value, str) and value.strip() for value in mapping.values()), f"{locale} empty translation")
    print(f"locale catalog: OK ({len(values)} source strings × 3 locales)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            write_catalog()
        check_catalog()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"LOCALE CATALOG FAILED: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
