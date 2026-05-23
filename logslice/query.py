"""Simple query parser and evaluator for filtering JSON log entries."""

import re
from dataclasses import dataclass
from typing import Any


OPERATORS = [">=", "<=", "!=", ">", "<", "="]


@dataclass
class Filter:
    field: str
    operator: str
    value: Any

    def match(self, record: dict) -> bool:
        actual = _get_nested(record, self.field)
        if actual is None:
            return False
        try:
            return _compare(actual, self.operator, self.value)
        except TypeError:
            return False


def parse_query(query_str: str) -> list[Filter]:
    """Parse a query string like 'level=error service=api latency>=200' into filters."""
    filters = []
    tokens = query_str.strip().split()
    for token in tokens:
        for op in OPERATORS:
            if op in token:
                parts = token.split(op, 1)
                if len(parts) == 2:
                    field, raw_value = parts[0].strip(), parts[1].strip()
                    value = _coerce(raw_value)
                    filters.append(Filter(field=field, operator=op, value=value))
                    break
    return filters


def apply_filters(record: dict, filters: list[Filter]) -> bool:
    """Return True if the record matches all filters."""
    return all(f.match(record) for f in filters)


def _get_nested(record: dict, field: str) -> Any:
    """Support dot-notation for nested fields, e.g. 'http.status'."""
    keys = field.split(".")
    current = record
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _coerce(value: str) -> Any:
    """Try to coerce string to int or float, otherwise keep as string."""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    ops = {
        "=": lambda a, b: str(a) == str(b) if not isinstance(b, (int, float)) else a == b,
        "!=": lambda a, b: str(a) != str(b) if not isinstance(b, (int, float)) else a != b,
        ">": lambda a, b: float(a) > float(b),
        "<": lambda a, b: float(a) < float(b),
        ">=": lambda a, b: float(a) >= float(b),
        "<=": lambda a, b: float(a) <= float(b),
    }
    fn = ops.get(operator)
    if fn is None:
        raise ValueError(f"Unknown operator: {operator}")
    return fn(actual, expected)
