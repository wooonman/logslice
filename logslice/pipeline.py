"""Build a processing pipeline from CLI / programmatic options."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.deduplicator import dedup_by, dedup_exact
from logslice.enricher import enrich_index, enrich_static, enrich_timestamp
from logslice.query import apply_filters, parse_query
from logslice.sampler import sample
from logslice.transformer import drop_fields, keep_fields, rename_fields

Record = Dict[str, Any]


def build_pipeline(
    records: Iterable[Record],
    *,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    # transformer options
    drop: Optional[List[str]] = None,
    keep: Optional[List[str]] = None,
    rename: Optional[Dict[str, str]] = None,
    # enricher options
    add_index: bool = False,
    add_timestamp_iso: bool = False,
    static_fields: Optional[Dict[str, Any]] = None,
    # dedup options
    dedup_fields: Optional[List[str]] = None,
    dedup_exact_match: bool = False,
    # sampler options
    sample_n: Optional[int] = None,
    sample_rate: Optional[float] = None,
) -> Iterator[Record]:
    """Chain transformations and return a lazy iterator of processed records."""
    stream: Iterable[Record] = records

    if query:
        filters = parse_query(query)
        stream = apply_filters(stream, filters)

    if drop:
        stream = drop_fields(stream, drop)

    if keep:
        stream = keep_fields(stream, keep)

    if rename:
        stream = rename_fields(stream, rename)

    if static_fields:
        stream = enrich_static(stream, static_fields)

    if add_timestamp_iso:
        stream = enrich_timestamp(stream)

    if add_index:
        stream = enrich_index(stream)

    if dedup_exact_match:
        stream = dedup_exact(stream)
    elif dedup_fields:
        stream = dedup_by(stream, dedup_fields)

    if sample_n is not None or sample_rate is not None:
        stream = sample(stream, every_n=sample_n, rate=sample_rate)

    if limit is not None:
        stream = _head(stream, limit)

    return stream  # type: ignore[return-value]


def _head(records: Iterable[Record], n: int) -> Iterator[Record]:
    for i, record in enumerate(records):
        if i >= n:
            break
        yield record
