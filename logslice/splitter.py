"""Split a stream of records into named buckets based on a field value or query."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional

from logslice.query import Filter, apply_filters, parse_query


def split_by_value(
    records: Iterable[dict],
    field: str,
    *,
    default_bucket: str = "__other__",
) -> Dict[str, List[dict]]:
    """Partition records into buckets keyed by the value of *field*.

    Records that lack *field* are placed in *default_bucket*.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        key = record.get(field)
        bucket = str(key) if key is not None else default_bucket
        buckets[bucket].append(record)
    return dict(buckets)


def split_by_query(
    records: Iterable[dict],
    queries: Dict[str, str],
    *,
    default_bucket: Optional[str] = None,
) -> Dict[str, List[dict]]:
    """Partition records using named query strings.

    Each record is placed in the *first* matching bucket.  If no query
    matches and *default_bucket* is given the record goes there; otherwise
    it is silently dropped.

    Args:
        records: Iterable of parsed JSON log records.
        queries: Mapping of bucket_name -> query string.
        default_bucket: Optional catch-all bucket name.
    """
    compiled: List[tuple[str, List[Filter]]] = [
        (name, parse_query(q)) for name, q in queries.items()
    ]
    buckets: Dict[str, List[dict]] = defaultdict(list)

    for record in records:
        placed = False
        for name, filters in compiled:
            if apply_filters(record, filters):
                buckets[name].append(record)
                placed = True
                break
        if not placed and default_bucket is not None:
            buckets[default_bucket].append(record)

    return dict(buckets)


def iter_bucket(
    records: Iterable[dict],
    field: str,
    value: str,
) -> Iterator[dict]:
    """Yield only records where *field* equals *value* (lazy version of split_by_value)."""
    for record in records:
        if str(record.get(field, "")) == value:
            yield record
