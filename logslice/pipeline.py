"""Build and execute a processing pipeline from CLI / API options."""

from __future__ import annotations

from typing import Iterable, Iterator

from logslice.query import apply_filters, parse_query
from logslice.sampler import sample
from logslice.ratelimiter import rate_limit


def _head(records: Iterable[dict], n: int) -> Iterator[dict]:
    for i, r in enumerate(records):
        if i >= n:
            break
        yield r


def build_pipeline(
    records: Iterable[dict],
    *,
    query: str | None = None,
    limit: int | None = None,
    sample_n: int | None = None,
    sample_prob: float | None = None,
    rate: int | None = None,
    rate_window: float = 1.0,
    throttle_interval: float | None = None,
) -> Iterator[dict]:
    """Wrap *records* in a chain of processing stages driven by options.

    Stages applied in order:
      1. Query filtering
      2. Sampling  (every-N or probability)
      3. Rate limiting  (sliding window)
      4. Throttle  (minimum inter-record interval)
      5. Limit  (hard cap on total records)

    Args:
        records: Source iterable of parsed JSON dicts.
        query: Optional filter expression (see :mod:`logslice.query`).
        limit: Stop after this many records.
        sample_n: Keep every *sample_n*-th record.
        sample_prob: Keep each record with this probability (0–1).
        rate: Maximum records per *rate_window* seconds.
        rate_window: Window size in seconds for rate limiting.
        throttle_interval: Minimum seconds between consecutive records.

    Yields:
        Processed records.
    """
    stream: Iterable[dict] = records

    if query:
        filters = parse_query(query)
        stream = apply_filters(stream, filters)

    if sample_n is not None or sample_prob is not None:
        stream = sample(stream, every_n=sample_n, probability=sample_prob)

    if rate is not None:
        from logslice.ratelimiter import rate_limit as _rl
        stream = _rl(stream, max_per_window=rate, window_seconds=rate_window)

    if throttle_interval is not None:
        from logslice.ratelimiter import throttle as _th
        stream = _th(stream, min_interval=throttle_interval)

    if limit is not None:
        stream = _head(stream, limit)

    yield from stream
