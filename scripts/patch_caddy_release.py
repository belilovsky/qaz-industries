#!/usr/bin/env python3
"""Safely update only the QAZ.INDUSTRIES block in the shared Caddyfile."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


RELEASE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
BLOCK_START_RE = re.compile(r"(?m)^qaz\.industries \{\n")
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; base-uri 'self'; frame-ancestors 'self'; object-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; form-action 'self'",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}
HEADER_RE = re.compile(
    r'(?m)^(?P<indent>[ \t]*)X-Qaz(?:-Industries)?-Release "[^"]+"$'
)
HEALTH_RE = re.compile(r'("service":"qaz-industries","release":")[^"]+(")')


def qaz_block(source: str) -> tuple[str, str, str]:
    """Return the prefix, top-level QAZ block, and suffix.

    Product blocks are top-level in the shared Caddyfile. Nested Caddy blocks
    are indented, so the first unindented closing brace ends this block.
    """

    matches = list(BLOCK_START_RE.finditer(source))
    if len(matches) != 1:
        raise ValueError("expected exactly one top-level qaz.industries block")
    start = matches[0].start()
    end = source.find("\n}\n", start)
    if end < 0:
        raise ValueError("qaz.industries block has no top-level closing brace")
    return source[:start], source[start : end + 3], source[end + 3 :]


def upsert_security_headers(block: str) -> str:
    """Keep product-owned security headers inside the QAZ header block."""

    match = re.search(r"(?m)^  header \{\n(?P<body>(?:    .*\n)*)^  \}\n", block)
    if not match:
        raise ValueError("QAZ header block is missing")
    body = match.group("body")
    for name, value in SECURITY_HEADERS.items():
        line_re = re.compile(rf"(?m)^(?P<indent>    ){re.escape(name)} \"[^\"]*\"$")
        matches = list(line_re.finditer(body))
        desired = f'    {name} "{value}"'
        if len(matches) > 1:
            raise ValueError(f"{name} appears more than once in QAZ header block")
        if matches:
            body = body[: matches[0].start()] + desired + body[matches[0].end() :]
        else:
            body += desired + "\n"
    return block[: match.start("body")] + body + block[match.end("body") :]


def ensure_line_after(block: str, line: str, anchor: str) -> str:
    """Insert one exact directive after an existing line, fail on duplicates."""

    line_re = re.compile(rf"(?m)^  {re.escape(line)}$")
    count = len(line_re.findall(block))
    if count > 1:
        raise ValueError(f"directive appears more than once: {line}")
    if count == 1:
        return block
    anchor_re = re.compile(rf"(?m)^{re.escape(anchor)}$\n")
    match = anchor_re.search(block)
    if not match:
        raise ValueError(f"anchor directive is missing: {anchor}")
    return block[: match.end()] + f"  {line}\n" + block[match.end() :]


def patch(source: str, release: str) -> str:
    if not RELEASE_RE.fullmatch(release):
        raise ValueError("release identifier must contain only letters, digits, '-' or '_'")

    prefix, block, suffix = qaz_block(source)
    if len(HEADER_RE.findall(block)) != 1:
        raise ValueError("expected exactly one QAZ release header in qaz.industries block")
    if len(HEALTH_RE.findall(block)) != 1:
        raise ValueError("expected exactly one QAZ health release marker in qaz.industries block")

    block = upsert_security_headers(block)
    block = HEADER_RE.sub(
        lambda match: f'{match.group("indent")}X-Qaz-Industries-Release "{release}"',
        block,
        count=1,
    )
    block = HEALTH_RE.sub(rf"\g<1>{release}\g<2>", block, count=1)
    block = ensure_line_after(
        block,
        'header @qaz_industries_health Content-Type application/json',
        '  @qaz_industries_health path /api/health',
    )
    block = ensure_line_after(
        block,
        'header @qaz_industries_health Cache-Control "no-store"',
        '  header @qaz_industries_health Content-Type application/json',
    )
    block = ensure_line_after(block, '@qaz_industries_release path /release.json', '  respond @qaz_industries_health `{"status":"ok","service":"qaz-industries","release":"' + release + '"}` 200')
    block = ensure_line_after(block, 'header @qaz_industries_release Cache-Control "no-store"', '  @qaz_industries_release path /release.json')

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
