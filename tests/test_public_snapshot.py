from __future__ import annotations

from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.public_snapshot import fetch_json, render_json, require_public_https, utc_timestamp, write_text_files


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


class PublicSnapshotTests(unittest.TestCase):
    def test_https_guard_rejects_credentials_and_cleartext(self):
        self.assertEqual(require_public_https("https://qgeo.tech/health"), "https://qgeo.tech/health")
        with self.assertRaises(ValueError):
            require_public_https("http://qgeo.tech/health")
        with self.assertRaises(ValueError):
            require_public_https("https://user:secret@qgeo.tech/health")

    def test_fetch_json_sets_contract_headers_and_timeout(self):
        observed = {}

        def opener(request, *, timeout):
            observed["url"] = request.full_url
            observed["accept"] = request.get_header("Accept")
            observed["agent"] = request.get_header("User-agent")
            observed["timeout"] = timeout
            return Response(json.dumps({"status": "ok"}).encode())

        self.assertEqual(fetch_json("https://example.org/health", opener=opener), {"status": "ok"})
        self.assertEqual(observed, {
            "url": "https://example.org/health",
            "accept": "application/json",
            "agent": "qaz-industries-snapshot/2.0",
            "timeout": 20,
        })

    def test_timestamp_and_json_are_deterministic(self):
        now = datetime(2026, 8, 9, 12, 30, 45, 999, tzinfo=timezone.utc)
        self.assertEqual(utc_timestamp(now), "2026-08-09T12:30:45Z")
        self.assertEqual(render_json({"значение": 1}), '{\n  "значение": 1\n}\n')

    def test_write_text_files_replaces_complete_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.json"
            second = root / "nested" / "second.json"
            first.write_text("old", encoding="utf-8")
            write_text_files({first: "new\n", second: "second\n"})
            self.assertEqual(first.read_text(encoding="utf-8"), "new\n")
            self.assertEqual(second.read_text(encoding="utf-8"), "second\n")


if __name__ == "__main__":
    unittest.main()
