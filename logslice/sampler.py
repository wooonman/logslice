"""Record sampling utilities — keep every Nth record or a random fraction."""

from __future__ import annotations

import random
from typing import Iterable, Iterator


def sample_every_n(
    records: Iterable[dict],
    n: int,
) -> Iterator[dict]:
    """Yield every *n*-th record (1-based counter).

    Args:
        records: Iterable of parsed JSON log records.
        n: Keep one record for every *n* seen.  Must be >= 1.

    Yields:
        Selected records.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    for i, record in enumerate(records, start=1):
        if i % n == 0:
            yield record


def sample_random(
    records: Iterable[dict],
    rate: float,
    seed: int | None = None,
) -> Iterator[dict]:
    """Yield each record with probability *rate*.

    Args:
        records: Iterable of parsed JSON log records.
        rate: Probability in the range (0, 1] that any given record is kept.
        seed: Optional RNG seed for reproducibility.

    Yields:
        Selected records.
    """
    if not 0 < rate <= 1.0:
        raise ValueError(f"rate must be in (0, 1], got {rate}")
    rng = random.Random(seed)
    for record in records:
        if rng.random() < rate:
            yield record


def sample(
    records: Iterable[dict],
    *,
    every_n: int | None = None,
    rate: float | None = None,
    seed: int | None = None,
) -> Iterator[dict]:
    """Convenience wrapper — choose either every-n or random-rate sampling.

    Exactly one of *every_n* or *rate* must be provided.
    """
    if (every_n is None) == (rate is None):
        raise ValueError("Provide exactly one of 'every_n' or 'rate'.")
    if every_n is not None:
        return sample_every_n(records, every_n)
    return sample_random(records, rate, seed=seed)  # type: ignore[arg-type]
