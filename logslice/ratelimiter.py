"""Rate-limit a stream of log records to at most N records per time window."""

from __future__ import annotations

import time
from collections import deque
from typing import Iterable, Iterator


def rate_limit(
    records: Iterable[dict],
    max_per_window: int,
    window_seconds: float = 1.0,
    *,
    _time_fn=time.monotonic,
    _sleep_fn=time.sleep,
) -> Iterator[dict]:
    """Yield records, blocking when the rate limit is exceeded.

    Args:
        records: Source iterable of log record dicts.
        max_per_window: Maximum number of records allowed per *window_seconds*.
        window_seconds: Length of the sliding window in seconds.
        _time_fn: Callable returning current time (injectable for tests).
        _sleep_fn: Callable used to sleep (injectable for tests).

    Yields:
        Records at a rate no higher than *max_per_window* per *window_seconds*.
    """
    if max_per_window < 1:
        raise ValueError("max_per_window must be >= 1")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be > 0")

    timestamps: deque[float] = deque()

    for record in records:
        now = _time_fn()
        cutoff = now - window_seconds

        # Drop timestamps outside the current window
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()

        if len(timestamps) >= max_per_window:
            # Sleep until the oldest timestamp falls out of the window
            sleep_for = timestamps[0] - cutoff
            if sleep_for > 0:
                _sleep_fn(sleep_for)
            # Re-prune after sleeping
            now = _time_fn()
            cutoff = now - window_seconds
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

        timestamps.append(_time_fn())
        yield record


def throttle(
    records: Iterable[dict],
    min_interval: float,
    *,
    _time_fn=time.monotonic,
    _sleep_fn=time.sleep,
) -> Iterator[dict]:
    """Ensure at least *min_interval* seconds between consecutive yielded records."""
    if min_interval < 0:
        raise ValueError("min_interval must be >= 0")

    last: float | None = None
    for record in records:
        if last is not None:
            elapsed = _time_fn() - last
            if elapsed < min_interval:
                _sleep_fn(min_interval - elapsed)
        last = _time_fn()
        yield record
