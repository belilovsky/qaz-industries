#!/usr/bin/env python3
"""Build and verify one disposable immutable release candidate."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commit = subprocess.check_output(
        ("git", "rev-parse", "HEAD"), cwd=ROOT, text=True
    ).strip()
    release = f"quality-{commit[:12]}"
    with tempfile.TemporaryDirectory(prefix="qaz-industries-build-") as temporary:
        output = Path(temporary) / "release"
        subprocess.run(
            (
                "python3",
                "scripts/build_release.py",
                "--release",
                release,
                "--output",
                str(output),
            ),
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            (
                "python3",
                "scripts/verify_release_artifact.py",
                "--directory",
                str(output),
                "--release",
                release,
                "--commit",
                commit,
            ),
            cwd=ROOT,
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
