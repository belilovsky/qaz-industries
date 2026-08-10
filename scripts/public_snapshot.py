"""Shared fail-closed helpers for reviewed public snapshot refresh scripts."""

from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Callable, Mapping
from urllib.parse import urlparse
from urllib.request import Request, urlopen


USER_AGENT = "qaz-industries-snapshot/2.0"


def require_public_https(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"public HTTPS URL required: {url!r}")
    return url


def fetch_json(
    url: str,
    *,
    timeout: int = 20,
    user_agent: str = USER_AGENT,
    opener: Callable[..., AbstractContextManager] = urlopen,
    attempts: int = 3,
) -> dict:
    if attempts < 1:
        raise ValueError("fetch attempts must be positive")
    request = Request(
        require_public_https(url),
        headers={"Accept": "application/json", "User-Agent": user_agent},
    )
    last_error: OSError | None = None
    for attempt in range(attempts):
        try:
            with opener(request, timeout=timeout) as response:  # nosec B310: URL is HTTPS-validated above
                payload = json.load(response)
            break
        except OSError as error:
            last_error = error
            if attempt + 1 == attempts:
                raise
            time.sleep(0.5 * (attempt + 1))
    else:  # pragma: no cover - defensive; the loop either returns data or raises
        raise last_error or RuntimeError(f"failed to fetch {url}")
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required from {url}")
    return payload


def utc_timestamp(now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return current.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render_json(payload: object, *, compact: bool = False) -> str:
    options = {"ensure_ascii": False}
    if compact:
        options["separators"] = (",", ":")
    else:
        options["indent"] = 2
    return json.dumps(payload, **options) + "\n"


def write_text_files(files: Mapping[Path, str]) -> None:
    staged: list[tuple[Path, Path]] = []
    try:
        for destination, content in files.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                delete=False,
            ) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
                staged.append((Path(handle.name), destination))
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def emit_snapshot(
    payload: dict,
    destination: Path,
    *,
    write: bool,
    extra_files: Mapping[Path, str] | None = None,
) -> None:
    rendered = render_json(payload)
    if not write:
        print(rendered, end="")
        return
    files = {destination: rendered, **(extra_files or {})}
    write_text_files(files)
    for path in files:
        print(f"updated {path}")
