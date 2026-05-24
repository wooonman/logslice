"""Truncate or cap fields in log records to limit verbosity."""

from __future__ import annotations

from typing import Any, Iterable, Iterator


def truncate_field(
    records: Iterable[dict],
    field: str,
    max_length: int,
    placeholder: str = "...",
) -> Iterator[dict]:
    """Truncate a string field to *max_length* characters.

    Non-string values and missing fields are left untouched.
    """
    if max_length < 0:
        raise ValueError("max_length must be >= 0")
    for record in records:
        rec = dict(record)
        value = rec.get(field)
        if isinstance(value, str) and len(value) > max_length:
            rec[field] = value[:max_length] + placeholder
        yield rec


def truncate_fields(
    records: Iterable[dict],
    limits: dict[str, int],
    placeholder: str = "...",
) -> Iterator[dict]:
    """Apply per-field length limits from a mapping of {field: max_length}."""
    for field, max_length in limits.items():
        if max_length < 0:
            raise ValueError(f"max_length for '{field}' must be >= 0")
    for record in records:
        rec = dict(record)
        for field, max_length in limits.items():
            value = rec.get(field)
            if isinstance(value, str) and len(value) > max_length:
                rec[field] = value[:max_length] + placeholder
        yield rec


def cap_list_field(
    records: Iterable[dict],
    field: str,
    max_items: int,
) -> Iterator[dict]:
    """Cap a list field to at most *max_items* elements.

    Non-list values and missing fields are left untouched.
    """
    if max_items < 0:
        raise ValueError("max_items must be >= 0")
    for record in records:
        rec = dict(record)
        value = rec.get(field)
        if isinstance(value, list) and len(value) > max_items:
            rec[field] = value[:max_items]
        yield rec
