#!/usr/bin/env python3
"""Validate AVDS visual baselines and compare captured PNGs without dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "avds-visual-regression.v1.json"
PAGES = ("index.html", "industry.html", "benchmarks.html", "publication.html")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def png_pixels(path: Path) -> tuple[int, int, int, bytes]:
    data = path.read_bytes()
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path}: PNG signature")
    offset = 8
    chunks: list[bytes] = []
    width = height = bit_depth = color_type = interlace = None
    while offset < len(data):
        require(offset + 12 <= len(data), f"{path}: truncated PNG chunk")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        require(payload_end + 4 <= len(data), f"{path}: invalid PNG chunk length")
        payload = data[payload_start:payload_end]
        if kind == b"IHDR":
            require(len(payload) == 13, f"{path}: invalid IHDR")
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            require(bit_depth == 8 and color_type in {2, 6} and compression == 0 and filtering == 0 and interlace == 0, f"{path}: unsupported PNG format")
        elif kind == b"IDAT":
            chunks.append(payload)
        elif kind == b"IEND":
            break
        offset = payload_end + 4
    require(width is not None and height is not None and color_type is not None, f"{path}: IHDR missing")
    channels = 4 if color_type == 6 else 3
    row_size = width * channels
    compressed = zlib.decompress(b"".join(chunks))
    expected = height * (row_size + 1)
    require(len(compressed) == expected, f"{path}: decoded PNG length mismatch")
    rows: list[bytes] = []
    cursor = 0
    previous = bytes(row_size)
    for _ in range(height):
        filter_type = compressed[cursor]
        current = bytearray(compressed[cursor + 1:cursor + 1 + row_size])
        cursor += row_size + 1
        for index in range(row_size):
            left = current[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                current[index] = (current[index] + left) & 255
            elif filter_type == 2:
                current[index] = (current[index] + up) & 255
            elif filter_type == 3:
                current[index] = (current[index] + ((left + up) // 2)) & 255
            elif filter_type == 4:
                predictor = left + up - upper_left
                distance_left = abs(predictor - left)
                distance_up = abs(predictor - up)
                distance_upper_left = abs(predictor - upper_left)
                nearest = left if distance_left <= distance_up and distance_left <= distance_upper_left else up if distance_up <= distance_upper_left else upper_left
                current[index] = (current[index] + nearest) & 255
            elif filter_type != 0:
                raise ValueError(f"{path}: unsupported PNG filter {filter_type}")
        rows.append(bytes(current))
        previous = bytes(current)
    return width, height, channels, b"".join(rows)


def png_info(path: Path) -> tuple[int, int, int]:
    """Read only the PNG header for the fast manifest gate."""
    data = path.read_bytes()
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path}: PNG signature")
    offset = 8
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        require(payload_end + 4 <= len(data), f"{path}: invalid PNG chunk length")
        if kind == b"IHDR":
            require(length == 13, f"{path}: invalid IHDR")
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", data[payload_start:payload_end])
            require(bit_depth == 8 and color_type in {2, 6} and compression == 0 and filtering == 0 and interlace == 0, f"{path}: unsupported PNG format")
            return width, height, 4 if color_type == 6 else 3
        offset = payload_end + 4
    raise ValueError(f"{path}: IHDR missing")


def validate_manifest(manifest: dict[str, object]) -> list[dict[str, object]]:
    require(manifest.get("schema_version") == "qaz-industries-avds-visual-regression-v1", "visual regression schema")
    require(manifest.get("product_id") == "qaz-industries", "visual regression product")
    require(manifest.get("routes") == list(PAGES), "visual regression route matrix")
    require(manifest.get("viewports") == [320, 1440], "visual regression viewport matrix")
    diff_policy = manifest.get("diff_policy")
    require(isinstance(diff_policy, dict) and 0 <= float(diff_policy.get("max_changed_pixel_ratio", -1)) <= 1, "visual diff policy")
    acceptance = manifest.get("acceptance")
    require(isinstance(acceptance, dict) and acceptance.get("status") == "verified" and "--compare" in acceptance.get("command", ""), "visual regression acceptance")
    baselines = manifest.get("baselines")
    require(isinstance(baselines, list) and len(baselines) == len(PAGES) * 2, "visual baseline count")
    seen: set[tuple[str, int]] = set()
    for item in baselines:
        require(isinstance(item, dict), "visual baseline entry")
        route = item.get("route")
        viewport = item.get("viewport")
        relative = item.get("file")
        require(route in PAGES and viewport in {320, 1440} and isinstance(relative, str), "visual baseline identity")
        require((route, viewport) not in seen, "duplicate visual baseline")
        seen.add((route, viewport))
        target = ROOT / relative
        require(target.is_file() and target.resolve().is_relative_to((ROOT / "tests" / "visual-baselines").resolve()), f"visual baseline file missing or unsafe: {relative}")
        require(item.get("sha256") == hashlib.sha256(target.read_bytes()).hexdigest(), f"visual baseline hash drift: {relative}")
        width, height, _ = png_info(target)
        require(item.get("width") == width and item.get("height") == height, f"visual baseline dimensions drift: {relative}")
    require(seen == {(route, viewport) for route in PAGES for viewport in (320, 1440)}, "visual baseline matrix incomplete")
    return [item for item in baselines if isinstance(item, dict)]


def compare(manifest: dict[str, object], baselines: list[dict[str, object]], actual_root: Path) -> None:
    threshold = float(manifest["diff_policy"]["max_changed_pixel_ratio"])
    for item in baselines:
        relative = str(item["file"])
        baseline = ROOT / relative
        actual = actual_root / Path(relative).name
        require(actual.is_file(), f"actual screenshot missing: {actual}")
        if hashlib.sha256(actual.read_bytes()).hexdigest() == item["sha256"]:
            continue
        bw, bh, bchannels, bpixels = png_pixels(baseline)
        aw, ah, achannels, apixels = png_pixels(actual)
        require((bw, bh, bchannels) == (aw, ah, achannels), f"visual dimensions or colour model drift: {actual.name}")
        changed = sum(left != right for left, right in zip(bpixels, apixels))
        ratio = changed / max(1, len(bpixels))
        require(ratio <= threshold, f"visual diff exceeds {threshold:.3%}: {actual.name} ({ratio:.3%})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare", action="store_true", help="compare current captures from --actual")
    parser.add_argument("--actual", type=Path, default=None, help="directory containing screenshots named like the baselines")
    args = parser.parse_args()
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        baselines = validate_manifest(manifest)
        if args.compare:
            require(args.actual is not None and args.actual.is_dir(), "--compare requires an actual screenshot directory")
            compare(manifest, baselines, args.actual)
            print(f"visual regression: OK ({len(baselines)} baselines compared)")
        else:
            print(f"visual regression manifest: OK ({len(baselines)} baselines)")
    except (OSError, TypeError, ValueError, json.JSONDecodeError, zlib.error, struct.error) as error:
        print(f"VISUAL REGRESSION CONTRACT FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
