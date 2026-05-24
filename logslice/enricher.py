"""Record enrichment: attach extra fields to log records from external sources."""

from __future__ import annotations

import datetime
import socket
from typing import Any, Dict, Iterable, Iterator, Optional

Record = Dict[str, Any]


def enrich_timestamp(
    records: Iterable[Record],
    source_field: str = "ts",
    dest_field: str = "timestamp_iso",
    *,
    unit: str = "s",
) -> Iterator[Record]:
    """Add an ISO-8601 string derived from a numeric epoch field.

    *unit* may be ``'s'`` (seconds, default) or ``'ms'`` (milliseconds).
    Records without *source_field* are yielded unchanged.
    """
    divisor = 1000.0 if unit == "ms" else 1.0
    for record in records:
        raw = record.get(source_field)
        if raw is None:
            yield record
            continue
        try:
            epoch = float(raw) / divisor
            dt = datetime.datetime.utcfromtimestamp(epoch)
            out = dict(record)
            out[dest_field] = dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
            yield out
        except (TypeError, ValueError, OSError):
            yield record


def enrich_hostname(
    records: Iterable[Record],
    field: str = "hostname",
    *,
    override: bool = False,
) -> Iterator[Record]:
    """Attach the local hostname to every record.

    If *field* already exists and *override* is False the record is
    yielded unchanged.
    """
    hostname = socket.gethostname()
    for record in records:
        if field in record and not override:
            yield record
            continue
        out = dict(record)
        out[field] = hostname
        yield out


def enrich_static(
    records: Iterable[Record],
    extra: Dict[str, Any],
    *,
    override: bool = False,
) -> Iterator[Record]:
    """Merge *extra* key-value pairs into every record.

    Existing keys are preserved unless *override* is True.
    """
    for record in records:
        out = dict(record)
        for k, v in extra.items():
            if k not in out or override:
                out[k] = v
        yield out


def enrich_index(
    records: Iterable[Record],
    field: str = "_index",
    *,
    start: int = 0,
) -> Iterator[Record]:
    """Add a sequential integer index to each record."""
    for i, record in enumerate(records, start=start):
        out = dict(record)
        out[field] = i
        yield out
