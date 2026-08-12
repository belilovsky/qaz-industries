#!/usr/bin/env python3
"""Dependency-free structural accessibility gate for every public HTML route."""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    parent: Node | None = None
    children: list[Node] = field(default_factory=list)
    text: list[str] = field(default_factory=list)

    def content(self) -> str:
        return " ".join(" ".join(self.text + [child.content() for child in self.children]).split())

    def ancestor(self, tag: str) -> Node | None:
        current = self.parent
        while current:
            if current.tag == tag:
                return current
            current = current.parent
        return None


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {})
        self.stack = [self.root]
        self.nodes: list[Node] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        if len(self.stack) > 1 and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.stack[-1].text.append(data)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def class_names(node: Node) -> set[str]:
    return set(node.attrs.get("class", "").split())


def check_page(page: str) -> None:
    parser = TreeParser()
    parser.feed((ROOT / page).read_text(encoding="utf-8"))
    parser.close()

    html = [node for node in parser.nodes if node.tag == "html"]
    require(len(html) == 1 and html[0].attrs.get("lang") == "ru", f"{page}: html lang must be ru")

    identified = [node for node in parser.nodes if node.attrs.get("id")]
    ids = [node.attrs["id"] for node in identified]
    require(len(ids) == len(set(ids)), f"{page}: duplicate id")
    id_set = set(ids)

    mains = [node for node in parser.nodes if node.tag == "main"]
    headings = [node for node in parser.nodes if node.tag == "h1"]
    require(len(mains) == 1 and mains[0].attrs.get("id"), f"{page}: exactly one identified main is required")
    require(len(headings) == 1 and headings[0].content(), f"{page}: exactly one non-empty h1 is required")

    skips = [node for node in parser.nodes if node.tag == "a" and "skip-link" in class_names(node)]
    require(len(skips) == 1, f"{page}: exactly one skip link is required")
    require(skips[0].attrs.get("href") == f"#{mains[0].attrs['id']}", f"{page}: skip link must target main")

    for node in parser.nodes:
        if node.tag == "nav":
            require(node.attrs.get("aria-label"), f"{page}: every nav requires aria-label")
        if node.tag == "button":
            require(node.attrs.get("type") == "button", f"{page}: button type must be explicit")
            require(node.attrs.get("aria-label") or node.content(), f"{page}: button requires an accessible name")
        if node.tag == "a":
            require(node.attrs.get("href"), f"{page}: anchor without href")
            require(node.attrs.get("aria-label") or node.content(), f"{page}: link requires an accessible name")
            if node.attrs.get("target") == "_blank":
                require("noreferrer" in node.attrs.get("rel", "").split(), f"{page}: external tab must use noreferrer")
        if node.tag == "img":
            require("alt" in node.attrs, f"{page}: image requires alt")
        if node.tag == "select":
            require(node.ancestor("label") is not None or node.attrs.get("aria-label"), f"{page}: select requires a label")
        if node.attrs.get("aria-controls"):
            require(node.attrs["aria-controls"] in id_set, f"{page}: aria-controls target is missing")
        if node.attrs.get("role") == "status":
            require(node.attrs.get("aria-live") in {"polite", "assertive"}, f"{page}: status requires aria-live")
        if "data-map-svg" in node.attrs:
            require(node.tag == "svg" and node.attrs.get("role") == "img" and node.attrs.get("aria-label"), f"{page}: map SVG requires image semantics")

    mobile_nav = next((node for node in identified if node.attrs["id"] == "mobile-nav"), None)
    require(mobile_nav is not None and "hidden" in mobile_nav.attrs, f"{page}: mobile navigation must start hidden")
    menu = next((node for node in parser.nodes if "menu-button" in class_names(node)), None)
    require(menu is not None and menu.attrs.get("aria-expanded") == "false", f"{page}: menu must start collapsed")


def main() -> int:
    try:
        for page in PAGES:
            check_page(page)
        avds = (ROOT / "avds.css").read_text(encoding="utf-8")
        require("@media (max-width: 720px)" in avds or "@media (max-width:720px)" in avds, "AV DS mobile target contract is missing")
        require("min-height: 44px" in avds or "min-height:44px" in avds, "AV DS mobile target size is missing")
        for page in PAGES:
            source = (ROOT / page).read_text(encoding="utf-8")
            require('name="viewport"' in source and "user-scalable=no" not in source, f"{page}: zoom must remain available")
    except (OSError, ValueError) as error:
        print(f"ACCESSIBILITY CHECK FAILED: {error}", file=sys.stderr)
        return 1
    print("accessibility contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
