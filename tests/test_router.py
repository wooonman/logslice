"""Tests for logslice.router."""

from __future__ import annotations

from typing import List

import pytest

from logslice.router import Route, make_route, route_records, split_by_field
from logslice.query import parse_query


def _records():
    return [
        {"level": "error", "msg": "boom", "service": "api"},
        {"level": "info", "msg": "ok", "service": "api"},
        {"level": "error", "msg": "oops", "service": "worker"},
        {"level": "debug", "msg": "trace", "service": "worker"},
    ]


def test_make_route_parses_query():
    sink_calls: List[dict] = []
    route = make_route("errors", "level=error", sink_calls.append)
    assert route.name == "errors"
    assert len(route.filters) == 1


def test_make_route_empty_query_no_filters():
    route = make_route("all", "", lambda r: None)
    assert route.filters == []


def test_route_records_sends_to_matching_sink():
    errors: List[dict] = []
    infos: List[dict] = []

    routes = [
        make_route("errors", "level=error", errors.append),
        make_route("infos", "level=info", infos.append),
    ]

    list(route_records(_records(), routes))

    assert len(errors) == 2
    assert len(infos) == 1
    assert all(r["level"] == "error" for r in errors)


def test_route_records_default_sink_receives_unmatched():
    unmatched: List[dict] = []
    routes = [make_route("errors", "level=error", lambda r: None)]

    list(route_records(_records(), routes, default_sink=unmatched.append))

    # info + debug go to default
    levels = {r["level"] for r in unmatched}
    assert "info" in levels
    assert "debug" in levels
    assert "error" not in levels


def test_route_records_yields_all_records():
    routes = [make_route("errors", "level=error", lambda r: None)]
    result = list(route_records(_records(), routes))
    assert len(result) == 4


def test_route_records_first_match_wins():
    bucket_a: List[dict] = []
    bucket_b: List[dict] = []

    routes = [
        make_route("a", "level=error", bucket_a.append),
        make_route("b", "level=error", bucket_b.append),
    ]

    list(route_records(_records(), routes))

    assert len(bucket_a) == 2
    assert len(bucket_b) == 0


def test_split_by_field_basic():
    buckets = split_by_field(_records(), "service")
    assert set(buckets.keys()) == {"api", "worker"}
    assert len(buckets["api"]) == 2
    assert len(buckets["worker"]) == 2


def test_split_by_field_missing_uses_sentinel():
    records = [{"msg": "no service"}, {"service": "api", "msg": "ok"}]
    buckets = split_by_field(records, "service")
    assert "__missing__" in buckets
    assert len(buckets["__missing__"]) == 1


def test_split_by_field_empty_stream():
    buckets = split_by_field([], "level")
    assert buckets == {}
