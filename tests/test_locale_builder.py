"""Regression tests for the local translation catalog generator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("locale_builder", ROOT / "scripts" / "build_locale_catalog.py")
assert SPEC and SPEC.loader
locale_builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(locale_builder)


class LocaleBuilderTests(unittest.TestCase):
    def test_write_reuses_verified_translation_without_network(self) -> None:
        original_catalog = locale_builder.CATALOG
        original_inventory = locale_builder.source_inventory
        original_translate = locale_builder.translate_batch
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "ui-locale.v1.json"
            destination.write_text(
                json.dumps(
                    {
                        "translations": {
                            "kk-KZ": {"Профили отраслей": "Сала профильдері"},
                            "en-US": {"Профили отраслей": "Industry profiles"},
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            try:
                locale_builder.CATALOG = destination
                locale_builder.source_inventory = lambda: ["Профили отраслей"]
                locale_builder.translate_batch = lambda *_args: self.fail("cached translation must not request a network refresh")
                locale_builder.write_catalog()
                result = json.loads(destination.read_text(encoding="utf-8"))
                self.assertEqual(result["translations"]["kk-KZ"]["Профили отраслей"], "Сала профильдері")
                self.assertEqual(result["translations"]["en-US"]["Профили отраслей"], "Industry profiles")
            finally:
                locale_builder.CATALOG = original_catalog
                locale_builder.source_inventory = original_inventory
                locale_builder.translate_batch = original_translate

    def test_avds_badge_label_is_translated_without_network(self) -> None:
        value = "Общее покрытие AVDS 4.6.0: 98 процентов; базовый маршрутный контракт: 92 процента"
        self.assertEqual(
            locale_builder.derived_translation(value, "kk-KZ"),
            "AVDS 4.6.0 жалпы қамтуы: 98 пайыз; негізгі маршруттық келісімшарт: 92 пайыз",
        )
        self.assertEqual(
            locale_builder.derived_translation(value, "en-US"),
            "AVDS 4.6.0 overall coverage: 98 percent; baseline route contract: 92 percent",
        )


if __name__ == "__main__":
    unittest.main()
