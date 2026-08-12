#!/usr/bin/env python3
"""Check WCAG contrast for AV DS semantic token pairs in every theme."""

from __future__ import annotations

import re
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "avds-tokens.css"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def luminance(hex_color: str) -> float:
    rgb = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(foreground: str, background: str) -> float:
    first, second = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def main() -> int:
    try:
        source = TOKENS.read_text(encoding="utf-8")
        required_themes = ("institutional", "editorial", "data-analytics", "map", "dark", "print")
        for theme in required_themes:
            selector = f'data-av-theme="{theme}"'
            require(selector in source, f"missing theme token block: {theme}")
        pairs = {
            "institutional": ("#020617", "#ffffff", "#1d4ed8"),
            "editorial": ("#241f1b", "#fffefa", "#8b4513"),
            "data-analytics": ("#082337", "#ffffff", "#006d9c"),
            "map": ("#0b2734", "#f9ffff", "#087f91"),
            "dark": ("#effcff", "#0d202d", "#6cecf0"),
            "print": ("#000000", "#ffffff", "#000000"),
        }
        for theme, (foreground, surface, primary) in pairs.items():
            for label, color in (("foreground", foreground), ("primary", primary)):
                require(re.fullmatch(r"#[0-9a-f]{6}", color), f"{theme}: {label} color format")
                require(ratio(color, surface) >= 4.5, f"{theme}: {label} contrast below 4.5:1")
    except (OSError, ValueError) as error:
        print(f"AVDS CONTRAST FAILED: {error}", file=sys.stderr)
        return 1
    print("AVDS contrast contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
