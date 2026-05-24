"""High-level watcher: tail one or more files, parse records, apply filters."""

from __future__ import annotations

import json
import threading
from typing import Callable, Generator, Sequence

from logslice.tail import tail_file
from logslice.query import Filter, apply_filters


Record = dict  # JSON object
Callback = Callable[[Record], None]


def watch_file(
    path: str,
    filters: Sequence[Filter] | None = None,
    from_start: bool = False,
    poll_interval: float = 0.25,
) -> Generator[Record, None, None]:
    """Yield parsed JSON records from a tailed file, optionally filtered."""
    _filters = list(filters or [])
    for raw in tail_file(path, poll_interval=poll_interval, from_start=from_start):
        raw = raw.strip()
        if not raw:
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        if _filters and not apply_filters(record, _filters):
            continue
        yield record


def watch_files_threaded(
    paths: Sequence[str],
    callback: Callback,
    filters: Sequence[Filter] | None = None,
    from_start: bool = False,
    poll_interval: float = 0.25,
) -> list[threading.Thread]:
    """Spawn a daemon thread per file; call *callback* for every matching record.

    Returns the list of started threads so the caller can join them if needed.
    """
    threads: list[threading.Thread] = []
    for path in paths:
        t = threading.Thread(
            target=_watch_worker,
            args=(path, callback, filters, from_start, poll_interval),
            daemon=True,
            name=f"watcher:{path}",
        )
        t.start()
        threads.append(t)
    return threads


def _watch_worker(
    path: str,
    callback: Callback,
    filters: Sequence[Filter] | None,
    from_start: bool,
    poll_interval: float,
) -> None:
    for record in watch_file(
        path,
        filters=filters,
        from_start=from_start,
        poll_interval=poll_interval,
    ):
        callback(record)
