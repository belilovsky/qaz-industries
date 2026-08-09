#!/usr/bin/env python3
"""Check local documentation links and index coverage."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = (ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "SECURITY.md", ROOT / "CONTRIBUTING.md")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def local_link(source: Path, reference: str) -> Path | None:
    value = reference.strip().strip("<>")
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    target = (source.parent / unquote(parsed.path)).resolve()
    require(ROOT.resolve() == target or ROOT.resolve() in target.parents, f"{source.name}: link escapes repository: {reference}")
    return target


def main() -> int:
    try:
        docs = sorted((ROOT / "docs").glob("*.md"))
        files = [*ENTRYPOINTS, *docs]
        for source in files:
            require(source.is_file(), f"missing documentation entrypoint: {source}")
            for reference in LINK.findall(source.read_text(encoding="utf-8")):
                target = local_link(source, reference)
                if target is not None:
                    require(target.is_file(), f"{source.relative_to(ROOT)}: broken link {reference}")

        index = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
        expected = {path.name for path in docs if path.name != "index.md"}
        indexed = {
            Path(urlsplit(reference.strip().strip("<>")).path).name
            for reference in LINK.findall(index)
            if urlsplit(reference.strip().strip("<>")).path.endswith(".md")
        }
        require(expected <= indexed, f"docs/index.md misses: {sorted(expected - indexed)}")
    except (OSError, ValueError) as error:
        print(f"DOCS CHECK FAILED: {error}", file=sys.stderr)
        return 1
    print(f"documentation links: OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
