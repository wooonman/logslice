"""Tests for logslice.fanout."""

from __future__ import annotations

import threading
from typing import Iterable, List

import pytest

from logslice.fanout import fanout, tee


def _records():
    return [
        {"level": "info", "msg": "a"},
        {"level": "error", "msg": "b"},
        {"level": "debug", "msg": "c"},
    ]


def test_tee_produces_n_copies():
    copies = tee(_records(), n=3)
    assert len(copies) == 3
    for copy in copies:
        assert len(copy) == 3


def test_tee_copies_are_independent():
    copies = tee(_records(), n=2)
    copies[0].append({"extra": True})
    assert len(copies[1]) == 3  # unaffected


def test_tee_single_copy():
    copies = tee(_records(), n=1)
    assert copies[0] == _records()


def test_tee_invalid_n_raises():
    with pytest.raises(ValueError):
        tee(_records(), n=0)


def test_tee_empty_stream():
    copies = tee([], n=2)
    assert copies == [[], []]


def test_fanout_all_consumers_receive_all_records():
    received: List[List[dict]] = [[], []]
    lock = threading.Lock()

    def make_consumer(idx: int):
        def _consume(stream: Iterable[dict]) -> None:
            for r in stream:
                with lock:
                    received[idx].append(r)
        return _consume

    fanout(_records(), [make_consumer(0), make_consumer(1)])

    assert len(received[0]) == 3
    assert len(received[1]) == 3


def test_fanout_no_consumers_drains_source():
    consumed = []

    def _gen():
        for r in _records():
            consumed.append(r)
            yield r

    fanout(_gen(), [])
    assert len(consumed) == 3


def test_fanout_single_consumer():
    result: List[dict] = []
    fanout(_records(), [lambda stream: result.extend(stream)])
    assert result == _records()


def test_fanout_consumers_run_concurrently():
    """Verify both consumers are invoked (thread-safety smoke test)."""
    counts = [0, 0]
    lock = threading.Lock()

    def make_consumer(idx: int):
        def _consume(stream: Iterable[dict]) -> None:
            for _ in stream:
                with lock:
                    counts[idx] += 1
        return _consume

    fanout(_records(), [make_consumer(0), make_consumer(1)])
    assert counts == [3, 3]
