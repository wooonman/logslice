"""High-level pipeline that wires reader → filter → sample → limit together."""

from __future__ import annotations

from typing import Iterable, Iterator

from logslice.query import apply_filters, parse_query
from logslice.sampler import sample


def build_pipeline(
    records: Iterable[dict],
    *,
    query: str = "",
    every_n: int | None = None,
    rate: float | None = None,
    seed: int | None = None,
    limit: int | None = None,
) -> Iterator[dict]:
    """Apply filtering, optional sampling, and optional limit to *records*.

    Args:
        records: Raw parsed JSON records from a reader.
        query:   Filter expression understood by :func:`parse_query`.
        every_n: If set, keep every *n*-th record after filtering.
        rate:    If set, keep each record with this probability after filtering.
        seed:    RNG seed forwarded to :func:`sample_random`.
        limit:   Stop after yielding this many records.

    Yields:
        Records that pass all stages.
    """
    filters = parse_query(query) if query else []
    stream: Iterable[dict] = apply_filters(records, filters)

    if every_n is not None or rate is not None:
        stream = sample(stream, every_n=every_n, rate=rate, seed=seed)

    count = 0
    for record in stream:
        if limit is not None and count >= limit:
            break
        yield record
        count += 1
