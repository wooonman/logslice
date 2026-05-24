"""Tests for logslice.sampler."""

from __future__ import annotations

import pytest

from logslice.sampler import sample, sample_every_n, sample_random


def _records(n: int = 10) -> list[dict]:
    return [{"i": i, "msg": f"line {i}"} for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# sample_every_n
# ---------------------------------------------------------------------------

def test_every_n_basic():
    result = list(sample_every_n(_records(10), n=2))
    assert [r["i"] for r in result] == [2, 4, 6, 8, 10]


def test_every_n_one_keeps_all():
    records = _records(5)
    assert list(sample_every_n(records, n=1)) == records


def test_every_n_larger_than_stream():
    result = list(sample_every_n(_records(5), n=10))
    assert result == []


def test_every_n_invalid_raises():
    with pytest.raises(ValueError, match="n must be"):
        list(sample_every_n(_records(), n=0))


def test_every_n_exactly_divisible():
    result = list(sample_every_n(_records(9), n=3))
    assert [r["i"] for r in result] == [3, 6, 9]


# ---------------------------------------------------------------------------
# sample_random
# ---------------------------------------------------------------------------

def test_random_rate_one_keeps_all():
    records = _records(20)
    result = list(sample_random(records, rate=1.0, seed=0))
    assert result == records


def test_random_rate_zero_invalid():
    with pytest.raises(ValueError, match="rate must be"):
        list(sample_random(_records(), rate=0.0))


def test_random_rate_above_one_invalid():
    with pytest.raises(ValueError, match="rate must be"):
        list(sample_random(_records(), rate=1.1))


def test_random_seed_reproducible():
    records = _records(50)
    a = list(sample_random(records, rate=0.4, seed=42))
    b = list(sample_random(records, rate=0.4, seed=42))
    assert a == b


def test_random_different_seeds_differ():
    records = _records(100)
    a = list(sample_random(records, rate=0.5, seed=1))
    b = list(sample_random(records, rate=0.5, seed=2))
    assert a != b


# ---------------------------------------------------------------------------
# sample (convenience wrapper)
# ---------------------------------------------------------------------------

def test_sample_every_n_via_wrapper():
    result = list(sample(_records(6), every_n=3))
    assert [r["i"] for r in result] == [3, 6]


def test_sample_rate_via_wrapper():
    records = _records(20)
    result = list(sample(records, rate=1.0))
    assert result == records


def test_sample_both_raises():
    with pytest.raises(ValueError, match="exactly one"):
        list(sample(_records(), every_n=2, rate=0.5))


def test_sample_neither_raises():
    with pytest.raises(ValueError, match="exactly one"):
        list(sample(_records()))
