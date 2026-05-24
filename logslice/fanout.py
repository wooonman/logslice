"""Fan a single record stream out to multiple independent consumers."""

from __future__ import annotations

import queue
import threading
from typing import Callable, Iterable, Iterator, List


def fanout(
    records: Iterable[dict],
    consumers: List[Callable[[Iterable[dict]], None]],
) -> None:
    """Feed *records* to every consumer concurrently.

    Each consumer receives its own independent iterator.  All consumers run in
    separate threads and this function blocks until every thread finishes.
    """
    n = len(consumers)
    if n == 0:
        # drain the source so callers don't have to
        for _ in records:
            pass
        return

    queues: List[queue.Queue] = [queue.Queue() for _ in range(n)]
    _SENTINEL = object()

    def _producer() -> None:
        for record in records:
            for q in queues:
                q.put(record)
        for q in queues:
            q.put(_SENTINEL)

    def _make_iter(q: queue.Queue) -> Iterator[dict]:
        while True:
            item = q.get()
            if item is _SENTINEL:
                return
            yield item

    threads = []
    for consumer, q in zip(consumers, queues):
        t = threading.Thread(target=consumer, args=(_make_iter(q),), daemon=True)
        threads.append(t)

    producer_thread = threading.Thread(target=_producer, daemon=True)
    producer_thread.start()
    for t in threads:
        t.start()

    producer_thread.join()
    for t in threads:
        t.join()


def tee(
    records: Iterable[dict],
    n: int = 2,
) -> List[List[dict]]:
    """Collect *records* into *n* independent lists (eager).

    Useful for testing or when you need multiple passes over the same data.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    buckets: List[List[dict]] = [[] for _ in range(n)]
    for record in records:
        for bucket in buckets:
            bucket.append(record)
    return buckets
