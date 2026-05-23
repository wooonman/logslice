"""Output formatting for log records."""

from __future__ import annotations

import json
from typing import Any


FORMATS = ("json", "pretty", "text")


def format_record(record: dict[str, Any], fmt: str = "json") -> str:
    """Format a single log record according to the chosen output format."""
    if fmt == "json":
        return json.dumps(record, ensure_ascii=False)
    elif fmt == "pretty":
        return json.dumps(record, indent=2, ensure_ascii=False)
    elif fmt == "text":
        return _format_text(record)
    else:
        raise ValueError(f"Unknown format {fmt!r}. Choose from: {', '.join(FORMATS)}")


def _format_text(record: dict[str, Any]) -> str:
    """Human-readable single-line text format.

    Tries to surface common fields (timestamp, level, message) first,
    then appends any remaining key=value pairs.
    """
    parts: list[str] = []

    for key in ("timestamp", "ts", "time", "@timestamp"):
        if key in record:
            parts.append(str(record[key]))
            break

    for key in ("level", "severity", "lvl"):
        if key in record:
            parts.append(f"[{str(record[key]).upper()}]")
            break

    for key in ("message", "msg", "text"):
        if key in record:
            parts.append(str(record[key]))
            break

    # Emit remaining fields as key=value
    skip = {"timestamp", "ts", "time", "@timestamp", "level", "severity", "lvl",
            "message", "msg", "text"}
    extras = " ".join(
        f"{k}={json.dumps(v, ensure_ascii=False)}"
        for k, v in record.items()
        if k not in skip
    )
    if extras:
        parts.append(extras)

    return " ".join(parts) if parts else json.dumps(record, ensure_ascii=False)
