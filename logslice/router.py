"""Route log records to different outputs based on field conditions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Iterator, List, Tuple

from logslice.query import Filter, apply_filters, parse_query


@dataclass
class Route:
    """A named route with a set of filters and a destination sink."""

    name: str
    filters: List[Filter]
    sink: Callable[[dict], None]


def make_route(
    name: str,
    query: str,
    sink: Callable[[dict], None],
) -> Route:
    """Build a Route from a query string."""
    filters = parse_query(query) if query else []
    return Route(name=name, filters=filters, sink=sink)


def route_records(
    records: Iterable[dict],
    routes: List[Route],
    default_sink: Callable[[dict], None] | None = None,
) -> Iterator[dict]:
    """Send each record to the first matching route's sink.

    If no route matches and *default_sink* is provided, it receives the record.
    Yields every record regardless so callers can still iterate.
    """
    for record in records:
        matched = False
        for route in routes:
            if apply_filters(record, route.filters):
                route.sink(record)
                matched = True
                break
        if not matched and default_sink is not None:
            default_sink(record)
        yield record


def split_by_field(
    records: Iterable[dict],
    field_name: str,
) -> Dict[str, List[dict]]:
    """Partition records into buckets keyed by the value of *field_name*.

    Records missing the field are placed under the key ``"__missing__"``.
    """
    buckets: Dict[str, List[dict]] = {}
    for record in records:
        key = str(record.get(field_name, "__missing__"))
        buckets.setdefault(key, []).append(record)
    return buckets
