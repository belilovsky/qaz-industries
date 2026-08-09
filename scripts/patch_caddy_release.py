#!/usr/bin/env python3
"""Safely update only the QAZ.INDUSTRIES block in the shared Caddyfile."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


RELEASE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
BLOCK_START = "qaz.industries {\n"
HEADER_RE = re.compile(
    r'(?m)^(?P<indent>[ \t]*)X-Qaz(?:-Industries)?-Release "[^"]+"$'
)
HEALTH_RE = re.compile(r'("service":"qaz-industries","release":")[^"]+(")')


def qaz_block(source: str) -> tuple[str, str, str]:
    """Return the prefix, top-level QAZ block, and suffix.

    Product blocks are top-level in the shared Caddyfile. Nested Caddy blocks
    are indented, so the first unindented closing brace ends this block.
    """

    if source.count(BLOCK_START) != 1:
        raise ValueError("expected exactly one top-level qaz.industries block")
    start = source.index(BLOCK_START)
    end = source.find("\n}\n", start)
    if end < 0:
        raise ValueError("qaz.industries block has no top-level closing brace")
    return source[:start], source[start : end + 3], source[end + 3 :]


def patch(source: str, release: str) -> str:
    if not RELEASE_RE.fullmatch(release):
        raise ValueError("release identifier must contain only letters, digits, '-' or '_'")

    prefix, block, suffix = qaz_block(source)
    if len(HEADER_RE.findall(block)) != 1:
        raise ValueError("expected exactly one QAZ release header in qaz.industries block")
    if len(HEALTH_RE.findall(block)) != 1:
        raise ValueError("expected exactly one QAZ health release marker in qaz.industries block")

    block = HEADER_RE.sub(
        lambda match: f'{match.group("indent")}X-Qaz-Industries-Release "{release}"',
        block,
        count=1,
    )
    block = HEALTH_RE.sub(rf"\g<1>{release}\g<2>", block, count=1)

    if 'X-Qaz-Release "' in block:
        raise ValueError("legacy shared release header remains in qaz.industries block")
    if len(re.findall(r'(?m)^\s*X-Qaz-Industries-Release "[^"]+"$', block)) != 1:
        raise ValueError("QAZ-specific release header was not written exactly once")
    return prefix + block + suffix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--release", required=True)
    args = parser.parse_args()

    try:
        result = patch(args.input.read_text(encoding="utf-8"), args.release)
        args.output.write_text(result, encoding="utf-8")
    except (OSError, ValueError) as error:
        raise SystemExit(f"Caddy release patch failed: {error}") from error
    print("qaz.industries Caddy marker: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
