"""Build a processing pipeline from a stream of records."""

from __future__ import annotations

from typing import Iterator

from logslice.query import parse_query, apply_filters
from logslice.sampler import sample
from logslice.deduplicator import dedup_exact, dedup_by
from logslice.merger import merge


def _head(records: Iterator[dict], n: int) -> Iterator[dict]:
    for i, r in enumerate(records):
        if i >= n:
            break
        yield r


def build_pipeline(
    records: Iterator[dict],
    query: str | None = None,
    limit: int | None = None,
    sample_n: int | None = None,
    sample_prob: float | None = None,
    dedup: bool = False,
    dedup_fields: list[str] | None = None,
    merge_streams: list[Iterator[dict]] | None = None,
    merge_key: str | None = "timestamp",
) -> Iterator[dict]:
    """Chain query, sampling, dedup and merge steps into a single pipeline."""

    if merge_streams:
        all_streams = [records, *merge_streams]
        records = merge(all_streams, key=merge_key)

    if query:
        filters = parse_query(query)
        records = apply_filters(records, filters)

    if sample_n is not None:
        records = sample(records, every_n=sample_n)
    elif sample_prob is not None:
        records = sample(records, probability=sample_prob)

    if dedup_fields:
        records = dedup_by(records, fields=dedup_fields)
    elif dedup:
        records = dedup_exact(records)

    if limit is not None:
        records = _head(records, limit)

    return records
