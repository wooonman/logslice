"""Redact or mask sensitive fields in log records."""

from __future__ import annotations

import re
from typing import Any, Iterable, Iterator

_MASK = "***"


def redact_fields(
    records: Iterable[dict],
    fields: list[str],
    mask: str = _MASK,
) -> Iterator[dict]:
    """Replace the value of each named field with *mask*."""
    field_set = set(fields)
    for record in records:
        out = dict(record)
        for key in field_set:
            if key in out:
                out[key] = mask
        yield out


def redact_pattern(
    records: Iterable[dict],
    pattern: str,
    mask: str = _MASK,
) -> Iterator[dict]:
    """Replace any string value matching *pattern* (regex) with *mask*."""
    rx = re.compile(pattern)

    def _scrub(value: Any) -> Any:
        if isinstance(value, str) and rx.search(value):
            return rx.sub(mask, value)
        return value

    for record in records:
        yield {k: _scrub(v) for k, v in record.items()}


def redact_partial(
    records: Iterable[dict],
    fields: list[str],
    keep_start: int = 0,
    keep_end: int = 0,
    mask: str = _MASK,
) -> Iterator[dict]:
    """Partially mask string values, preserving leading/trailing characters."""
    field_set = set(fields)

    def _partial(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        n = len(value)
        start = min(keep_start, n)
        end = min(keep_end, n - start)
        if end:
            return value[:start] + mask + value[n - end :]
        return value[:start] + mask

    for record in records:
        out = dict(record)
        for key in field_set:
            if key in out:
                out[key] = _partial(out[key])
        yield out


def redact(records: Iterable[dict], **kwargs) -> Iterator[dict]:
    """Convenience wrapper — dispatches to the appropriate redaction function.

    Keyword arguments are forwarded to :func:`redact_fields`.
    """
    fields = kwargs.pop("fields", [])
    mask = kwargs.pop("mask", _MASK)
    return redact_fields(records, fields=fields, mask=mask)
