"""Field transformation utilities for log records."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]
TransformFn = Callable[[Any], Any]


def rename_fields(records: Iterable[Record], mapping: Dict[str, str]) -> Iterator[Record]:
    """Yield records with fields renamed according to *mapping* {old: new}."""
    for record in records:
        out = {}
        for key, value in record.items():
            out[mapping.get(key, key)] = value
        yield out


def drop_fields(records: Iterable[Record], fields: List[str]) -> Iterator[Record]:
    """Yield records with the specified *fields* removed."""
    drop = set(fields)
    for record in records:
        yield {k: v for k, v in record.items() if k not in drop}


def keep_fields(records: Iterable[Record], fields: List[str]) -> Iterator[Record]:
    """Yield records containing only the specified *fields*."""
    keep = set(fields)
    for record in records:
        yield {k: v for k, v in record.items() if k in keep}


def add_field(
    records: Iterable[Record],
    field: str,
    value_fn: Callable[[Record], Any],
) -> Iterator[Record]:
    """Yield records with a new *field* whose value is produced by *value_fn*."""
    for record in records:
        out = dict(record)
        out[field] = value_fn(record)
        yield out


def map_field(
    records: Iterable[Record],
    field: str,
    fn: TransformFn,
    *,
    missing_ok: bool = True,
) -> Iterator[Record]:
    """Apply *fn* to the value of *field* in every record.

    If *field* is absent and *missing_ok* is True the record is yielded
    unchanged; otherwise a KeyError is raised.
    """
    for record in records:
        if field not in record:
            if missing_ok:
                yield record
                continue
            raise KeyError(f"Field '{field}' not found in record: {record}")
        out = dict(record)
        out[field] = fn(record[field])
        yield out


def flatten(
    records: Iterable[Record],
    nested_field: str,
    *,
    prefix: Optional[str] = None,
    drop_original: bool = True,
) -> Iterator[Record]:
    """Hoist keys from a nested dict *nested_field* into the top-level record."""
    pfx = prefix if prefix is not None else f"{nested_field}_"
    for record in records:
        out = dict(record)
        nested = out.pop(nested_field, None) if drop_original else out.get(nested_field)
        if isinstance(nested, dict):
            for k, v in nested.items():
                out[f"{pfx}{k}"] = v
        elif nested is not None and not drop_original:
            pass
        elif nested is not None:
            out[nested_field] = nested
        yield out
