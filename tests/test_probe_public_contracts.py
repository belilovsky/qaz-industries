from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.probe_public_contracts import run_probe, validate_qazlake_snapshot


NOW = datetime(2026, 8, 26, tzinfo=timezone.utc)


def snapshot(retrieved_at: str = "2026-08-13T10:45:38Z") -> dict:
    return {
        "schema_version": "qaz-industries-qazlake-public-snapshot-v1",
        "status": "ready",
        "retrieved_at": retrieved_at,
        "indicators": [
            {"id": "one", "is_forecast": False},
            {"id": "two", "is_forecast": False},
            {"id": "three", "is_forecast": False},
        ],
    }


class PublicContractProbePolicyTests(unittest.TestCase):
    def test_valid_snapshot_age_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "snapshot.json"
            path.write_text(json.dumps(snapshot()), encoding="utf-8")
            self.assertEqual(validate_qazlake_snapshot(path, now=NOW), 12)

    def test_stale_snapshot_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "snapshot.json"
            path.write_text(json.dumps(snapshot("2026-07-01T00:00:00Z")), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stale"):
                validate_qazlake_snapshot(path, now=NOW)

    def test_malformed_snapshot_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "snapshot.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema"):
                validate_qazlake_snapshot(path, now=NOW)

    def test_qazlake_outage_is_non_blocking_with_current_snapshot(self) -> None:
        failed = subprocess.CompletedProcess(("probe",), 1, "", "not ready")
        with tempfile.TemporaryDirectory() as temporary, patch(
            "scripts.probe_public_contracts.validate_qazlake_snapshot", return_value=12
        ):
            result = run_probe("qazlake", ("probe",), Path(temporary), runner=lambda *args, **kwargs: failed)
        self.assertEqual(result["state"], "degraded")
        self.assertFalse(result["blocking"])

    def test_required_probe_failure_is_blocking(self) -> None:
        failed = subprocess.CompletedProcess(("probe",), 1, "", "release drift")
        with tempfile.TemporaryDirectory() as temporary:
            result = run_probe("sector-sources", ("probe",), Path(temporary), runner=lambda *args, **kwargs: failed)
        self.assertEqual(result["state"], "blocked")
        self.assertTrue(result["blocking"])


if __name__ == "__main__":
    unittest.main()
