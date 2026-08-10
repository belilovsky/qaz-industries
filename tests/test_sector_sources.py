from __future__ import annotations

import unittest

from scripts.check_sector_sources import indexed_count, require_release, selected_count


class SectorSourceContractTests(unittest.TestCase):
    def test_machine_index_counts_space_records_without_html_copy(self):
        payload = {
            "files": [
                {"id": "entities", "count": 32},
                {"id": "claims", "count": 143},
                {"id": "sources", "count": 116},
            ]
        }
        self.assertEqual(indexed_count(payload, "entities"), 32)
        self.assertEqual(indexed_count(payload, "claims"), 143)
        self.assertEqual(indexed_count(payload, "sources"), 116)

    def test_missing_machine_index_entry_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "sources"):
            indexed_count({"files": [{"id": "entities", "count": 32}]}, "sources")

    def test_release_and_thematic_module_contracts_fail_closed(self):
        self.assertEqual(
            require_release("2026-08-10.1", "2026-08-10.1", "farm"),
            "2026-08-10.1",
        )
        with self.assertRaisesRegex(ValueError, "differs"):
            require_release("2026-08-09.15", "2026-08-10.1", "farm")
        self.assertEqual(
            selected_count(
                {"modules": [{"id": "source-status", "record_count": 57}]},
                "source-status",
            ),
            57,
        )


if __name__ == "__main__":
    unittest.main()
