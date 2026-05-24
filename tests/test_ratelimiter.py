"""Tests for logslice.ratelimiter."""

from __future__ import annotations

import pytest

from logslice.ratelimiter import rate_limit, throttle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _records(n: int = 10) -> list[dict]:
    return [{"i": i, "msg": f"record {i}"} for i in range(n)]


class _FakeClock:
    """Monotonically advancing fake clock; auto-advances on each call."""

    def __init__(self, start: float = 0.0, step: float = 0.0):
        self._t = start
        self._step = step
        self.slept: list[float] = []

    def time(self) -> float:
        t = self._t
        self._t += self._step
        return t

    def advance(self, delta: float) -> None:
        self._t += delta

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self._t += seconds


# ---------------------------------------------------------------------------
# rate_limit
# ---------------------------------------------------------------------------

def test_rate_limit_yields_all_records_when_under_limit():
    clock = _FakeClock(step=0.2)  # 0.2 s between records, window=1 s, max=10
    result = list(rate_limit(_records(5), max_per_window=10, window_seconds=1.0,
                              _time_fn=clock.time, _sleep_fn=clock.sleep))
    assert len(result) == 5
    assert clock.slept == []


def test_rate_limit_sleeps_when_limit_reached():
    clock = _FakeClock(step=0.0)  # time does NOT advance unless we sleep
    result = list(rate_limit(_records(5), max_per_window=3, window_seconds=1.0,
                              _time_fn=clock.time, _sleep_fn=clock.sleep))
    assert len(result) == 5
    assert len(clock.slept) > 0  # had to sleep at least once


def test_rate_limit_invalid_max_raises():
    with pytest.raises(ValueError, match="max_per_window"):
        list(rate_limit(_records(1), max_per_window=0))


def test_rate_limit_invalid_window_raises():
    with pytest.raises(ValueError, match="window_seconds"):
        list(rate_limit(_records(1), max_per_window=1, window_seconds=0))


def test_rate_limit_empty_stream():
    result = list(rate_limit([], max_per_window=5))
    assert result == []


def test_rate_limit_preserves_record_content():
    clock = _FakeClock(step=0.5)
    recs = _records(3)
    result = list(rate_limit(recs, max_per_window=10, window_seconds=1.0,
                              _time_fn=clock.time, _sleep_fn=clock.sleep))
    assert result == recs


# ---------------------------------------------------------------------------
# throttle
# ---------------------------------------------------------------------------

def test_throttle_yields_all_records():
    clock = _FakeClock(step=0.5)
    result = list(throttle(_records(4), min_interval=0.1,
                            _time_fn=clock.time, _sleep_fn=clock.sleep))
    assert len(result) == 4


def test_throttle_sleeps_when_too_fast():
    clock = _FakeClock(step=0.0)  # time never advances on its own
    result = list(throttle(_records(3), min_interval=0.5,
                            _time_fn=clock.time, _sleep_fn=clock.sleep))
    assert len(result) == 3
    # First record has no predecessor — no sleep; subsequent two should sleep
    assert len(clock.slept) == 2


def test_throttle_zero_interval_no_sleep():
    clock = _FakeClock(step=0.0)
    list(throttle(_records(5), min_interval=0.0,
                  _time_fn=clock.time, _sleep_fn=clock.sleep))
    assert clock.slept == []


def test_throttle_negative_interval_raises():
    with pytest.raises(ValueError, match="min_interval"):
        list(throttle(_records(1), min_interval=-1.0))


def test_throttle_empty_stream():
    result = list(throttle([], min_interval=1.0))
    assert result == []
