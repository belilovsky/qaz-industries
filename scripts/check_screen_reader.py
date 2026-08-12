#!/usr/bin/env python3
"""Fail closed on the AVDS screen-reader semantic contract."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")
CONTRACT = ROOT / "data" / "avds-accessibility-contract.v1.json"
INTERACTIVE = {"a", "button", "input", "select", "textarea", "summary"}


class Node:
    def __init__(self, tag: str, attrs: dict[str, str], parent: "Node | None") -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list[Node] = []
        self.text: list[str] = []

    def content(self) -> str:
        return " ".join(" ".join(self.text + [child.content() for child in self.children]).split())


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {}, None)
        self.stack = [self.root]
        self.nodes: list[Node] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.stack[-1].text.append(data)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def ids(nodes: list[Node]) -> set[str]:
    return {node.attrs["id"] for node in nodes if node.attrs.get("id")}


def accessible_name(node: Node) -> str:
    return " ".join(
        part for part in (
            node.attrs.get("aria-label", ""),
            node.attrs.get("title", ""),
            node.content(),
        ) if part
    ).strip()


def check_page(page: str) -> None:
    parser = TreeParser()
    parser.feed((ROOT / page).read_text(encoding="utf-8"))
    parser.close()
    nodes = parser.nodes
    id_set = ids(nodes)
    require(any(node.tag == "main" and node.attrs.get("id") for node in nodes), f"{page}: identified main landmark missing")
    require(any(node.tag == "footer" for node in nodes), f"{page}: footer landmark missing")
    require(any(node.tag == "nav" and node.attrs.get("aria-label") for node in nodes), f"{page}: named navigation missing")

    for node in nodes:
        attrs = node.attrs
        if node.tag in INTERACTIVE or attrs.get("role") in {"button", "link", "tab", "menuitem"}:
            require(accessible_name(node), f"{page}: unnamed {node.tag} or {attrs.get('role', 'interactive')} surface")
        if attrs.get("aria-hidden") == "true":
            require("tabindex" not in attrs or attrs.get("tabindex") == "-1", f"{page}: aria-hidden surface must not be tabbable")
            require(node.tag not in INTERACTIVE and attrs.get("role") not in {"button", "link", "tab", "menuitem"}, f"{page}: interactive surface is aria-hidden")
        for relationship in ("aria-controls", "aria-labelledby", "aria-describedby"):
            if attrs.get(relationship):
                for target in re.split(r"\s+", attrs[relationship].strip()):
                    require(target in id_set, f"{page}: {relationship} target missing: {target}")
        if attrs.get("role") == "status":
            require(attrs.get("aria-live") in {"polite", "assertive"}, f"{page}: status live region missing")
        if attrs.get("data-av-icon"):
            require(attrs.get("aria-hidden") == "true", f"{page}: icon glyph must be aria-hidden")
        if node.tag == "svg":
            require(attrs.get("role") == "img" and accessible_name(node), f"{page}: SVG must be named image")
        if node.tag == "img":
            require("alt" in attrs, f"{page}: image alt attribute missing")

    live_ids = {node.attrs.get("id") for node in nodes if node.attrs.get("aria-live") in {"polite", "assertive"}}
    required_live = {
        "index.html": {"filter-summary", "hero-map-inspector", "map-inspector"},
        "industry.html": {"pulse-status", "territory-status", "layer-registry-status", "pulse-boundary-state", "coverage-chart"},
    }.get(page, set())
    require(required_live <= live_ids, f"{page}: required live regions missing: {sorted(required_live - live_ids)}")


def main() -> int:
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        require(contract.get("schema_version") == "qaz-industries-avds-accessibility-contract-v1", "screen-reader contract schema")
        require(contract.get("acceptance", {}).get("status") == "verified", "screen-reader contract is not verified")
        require(set(contract.get("routes", [])) == set(PAGES), "screen-reader route matrix")
        requirements = contract.get("requirements", {})
        require(len(requirements) == 7 and all(isinstance(value, str) and value for value in requirements.values()), "screen-reader requirements")
        for page in PAGES:
            check_page(page)
        map_source = (ROOT / "qazgeo-map.js").read_text(encoding="utf-8")
        require('path.setAttribute("tabindex", "0")' in map_source, "map regions are not keyboard focusable")
        require('path.setAttribute("aria-label"' in map_source, "map regions have no announced name")
        require("keydown" in map_source, "map keyboard handler is missing")
        locale_source = (ROOT / "locale.js").read_text(encoding="utf-8")
        require("snapshotState" in locale_source and "message" in locale_source, "state copy is not available to screen readers")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"SCREEN-READER CONTRACT FAILED: {error}", file=sys.stderr)
        return 1
    print("screen-reader contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
