"""Build a processing pipeline from a set of options."""

from __future__ import annotations

from typing import Iterable, Iterator

from logslice.deduplicator import dedup_exact
from logslice.query import apply_filters, parse_query
from logslice.sampler import sample
from logslice.truncator import truncate_fields


def _head(records: Iterable[dict], n: int) -> Iterator[dict]:
    for i, rec in enumerate(records):
        if i >= n:
            break
        yield rec


def build_pipeline(
    records: Iterable[dict],
    *,
    query: str | None = None,
    limit: int | None = None,
    dedup: bool = False,
    sample_rate: float | None = None,
    sample_n: int | None = None,
    truncate: dict[str, int] | None = None,
) -> Iterator[dict]:
    """Compose a pipeline of transformations over *records*.

    Parameters
    ----------
    records:     Source iterable of parsed log dicts.
    query:       Optional filter expression (see ``parse_query``).
    limit:       Stop after this many records.
    dedup:       Remove exact duplicate records.
    sample_rate: Keep each record with this probability (0.0–1.0).
    sample_n:    Keep every N-th record.
    truncate:    Mapping of {field: max_length} passed to ``truncate_fields``.
    """
    stream: Iterable[dict] = records

    if query:
        filters = parse_query(query)
        stream = apply_filters(stream, filters)

    if truncate:
        stream = truncate_fields(stream, truncate)

    if dedup:
        stream = dedup_exact(stream)

    if sample_rate is not None or sample_n is not None:
        stream = sample(stream, every_n=sample_n, probability=sample_rate)

    if limit is not None:
        stream = _head(stream, limit)

    return iter(stream)
