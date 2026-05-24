"""Export filtered log records to various output formats (JSONL, CSV, TSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Iterable, Iterator, List, Optional


def to_jsonl(records: Iterable[dict]) -> Iterator[str]:
    """Yield each record as a compact JSON line."""
    for record in records:
        yield json.dumps(record, separators=(",", ":"))


def to_csv(
    records: Iterable[dict],
    fields: List[str],
    delimiter: str = ",",
    missing: str = "",
) -> Iterator[str]:
    """Yield CSV/TSV rows (header first) for the given field names."""
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=delimiter)

    # header
    writer.writerow(fields)
    yield buf.getvalue().rstrip("\r\n")

    for record in records:
        buf.seek(0)
        buf.truncate(0)
        row = [_get(record, f, missing) for f in fields]
        writer.writerow(row)
        yield buf.getvalue().rstrip("\r\n")


def export(
    records: Iterable[dict],
    fmt: str = "jsonl",
    fields: Optional[List[str]] = None,
    missing: str = "",
) -> Iterator[str]:
    """Dispatch to the appropriate exporter.

    Supported formats: ``jsonl``, ``csv``, ``tsv``.
    """
    fmt = fmt.lower()
    if fmt == "jsonl":
        yield from to_jsonl(records)
    elif fmt in ("csv", "tsv"):
        if not fields:
            raise ValueError("fields must be provided for csv/tsv export")
        delimiter = "\t" if fmt == "tsv" else ","
        yield from to_csv(records, fields, delimiter=delimiter, missing=missing)
    else:
        raise ValueError(f"unsupported export format: {fmt!r}")


def _get(record: dict, field: str, default: str = "") -> str:
    """Return a string value for *field*, supporting dotted paths."""
    parts = field.split(".")
    val = record
    for part in parts:
        if not isinstance(val, dict):
            return default
        val = val.get(part)
        if val is None:
            return default
    return str(val)
