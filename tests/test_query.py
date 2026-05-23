"""Tests for the query parser and filter logic."""

import pytest
from logslice.query import Filter, apply_filters, parse_query


def test_parse_simple_equality():
    filters = parse_query("level=error")
    assert len(filters) == 1
    assert filters[0].field == "level"
    assert filters[0].operator == "="
    assert filters[0].value == "error"


def test_parse_numeric_operator():
    filters = parse_query("latency>=200")
    assert filters[0].operator == ">="
    assert filters[0].value == 200


def test_parse_multiple_filters():
    filters = parse_query("level=error service=api latency>100")
    assert len(filters) == 3


def test_parse_empty_query():
    assert parse_query("") == []


def test_filter_match_equality():
    f = Filter(field="level", operator="=", value="error")
    assert f.match({"level": "error"})
    assert not f.match({"level": "info"})


def test_filter_match_greater_than():
    f = Filter(field="latency", operator=">", value=100)
    assert f.match({"latency": 200})
    assert not f.match({"latency": 50})


def test_filter_missing_field():
    f = Filter(field="missing", operator="=", value="x")
    assert not f.match({"level": "info"})


def test_filter_nested_field():
    f = Filter(field="http.status", operator="=", value=404)
    assert f.match({"http": {"status": 404}})
    assert not f.match({"http": {"status": 200}})


def test_apply_filters_all_match():
    filters = parse_query("level=error service=api")
    record = {"level": "error", "service": "api", "latency": 300}
    assert apply_filters(record, filters)


def test_apply_filters_partial_match():
    filters = parse_query("level=error service=web")
    record = {"level": "error", "service": "api"}
    assert not apply_filters(record, filters)


def test_apply_filters_empty():
    assert apply_filters({"level": "info"}, []) is True
