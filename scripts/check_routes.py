#!/usr/bin/env python3
"""Check local HTML references and discovery files before a release."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "industry.html", "benchmarks.html")


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def local_target(reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith("//"):
        return None
    if not parsed.path:
        return None
    relative = unquote(parsed.path.lstrip("/"))
    target = (ROOT / relative).resolve()
    root = ROOT.resolve()
    if root not in target.parents and target != root:
        raise ValueError(f"reference escapes repository: {reference}")
    return target


def main() -> int:
    try:
        for page in PAGES:
            parser = ReferenceParser()
            parser.feed((ROOT / page).read_text(encoding="utf-8"))
            parser.close()
            for reference in parser.references:
                target = local_target(reference)
                if target is not None and not target.is_file():
                    raise ValueError(f"{page}: missing local reference {reference}")

        sitemap_root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        locations = {node.text for node in sitemap_root.findall(f"{ns}url/{ns}loc")}
        expected = {
            "https://qaz.industries/",
            "https://qaz.industries/industry.html",
            "https://qaz.industries/benchmarks.html",
        }
        if locations != expected:
            raise ValueError(f"sitemap URLs differ from canonical public set: {sorted(locations)}")
        if "Sitemap: https://qaz.industries/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
            raise ValueError("robots.txt: sitemap declaration missing")
    except (OSError, ET.ParseError, ValueError) as error:
        print(f"route hygiene: FAILED: {error}")
        return 1
    print("route hygiene: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
