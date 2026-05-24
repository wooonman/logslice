"""Build a processing pipeline from CLI / programmatic options."""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from logslice.query import parse_query, apply_filters
from logslice.sampler import sample
from logslice.deduplicator import dedup_exact, dedup_by
from logslice.redactor import redact_fields, redact_pattern


def _head(records: Iterable[dict], n: int) -> Iterator[dict]:
    for i, record in enumerate(records):
        if i >= n:
            break
        yield record


def build_pipeline(records: Iterable[dict], options: Any) -> Iterator[dict]:
    """Apply a chain of transforms driven by *options* (argparse Namespace or dict).

    Supported option attributes
    ---------------------------
    query        : str   – filter expression
    limit        : int   – max records to emit
    sample_n     : int   – keep every N-th record
    dedup        : bool  – exact-dedup on full record
    dedup_by     : list  – dedup by named fields
    redact       : list  – field names to redact
    redact_pattern: str  – regex pattern to redact from string values
    """
    if isinstance(options, dict):
        get = options.get
    else:
        get = lambda k, d=None: getattr(options, k, d)  # noqa: E731

    stream: Iterable[dict] = records

    query = get("query")
    if query:
        filters = parse_query(query)
        stream = apply_filters(stream, filters)

    sample_n = get("sample_n")
    if sample_n and sample_n > 1:
        stream = sample(stream, every_n=sample_n)

    if get("dedup"):
        stream = dedup_exact(stream)

    dedup_fields = get("dedup_by")
    if dedup_fields:
        stream = dedup_by(stream, fields=dedup_fields)

    redact_flds = get("redact")
    if redact_flds:
        stream = redact_fields(stream, fields=redact_flds)

    rx = get("redact_pattern")
    if rx:
        stream = redact_pattern(stream, pattern=rx)

    limit = get("limit")
    if limit and limit > 0:
        stream = _head(stream, limit)

    return stream
