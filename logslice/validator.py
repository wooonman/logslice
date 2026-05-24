"""Validate structured log records against a simple schema definition."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional

# Map of type-name strings to Python types for schema declarations
_TYPE_MAP: Dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}


def _check_field(
    record: Dict[str, Any],
    field: str,
    expected_type: Optional[str],
    required: bool,
) -> List[str]:
    """Return a list of validation error strings for a single field."""
    errors: List[str] = []
    if field not in record:
        if required:
            errors.append(f"missing required field '{field}'")
        return errors
    if expected_type is not None:
        py_type = _TYPE_MAP.get(expected_type)
        if py_type is None:
            errors.append(f"unknown type '{expected_type}' for field '{field}'")
        elif not isinstance(record[field], py_type):
            actual = type(record[field]).__name__
            errors.append(
                f"field '{field}' expected {expected_type}, got {actual}"
            )
    return errors


def validate_record(
    record: Dict[str, Any],
    schema: Dict[str, Any],
) -> List[str]:
    """Validate *record* against *schema*.

    *schema* is a mapping of field names to a dict with optional keys:
        - ``type``     (str)  – expected type name, e.g. ``"str"``
        - ``required`` (bool) – default ``False``

    Returns a (possibly empty) list of human-readable error strings.
    """
    errors: List[str] = []
    for field, rules in schema.items():
        required = rules.get("required", False)
        expected_type = rules.get("type")
        errors.extend(_check_field(record, field, expected_type, required))
    return errors


def filter_valid(
    records: Iterable[Dict[str, Any]],
    schema: Dict[str, Any],
    *,
    drop_invalid: bool = True,
) -> Iterator[Dict[str, Any]]:
    """Yield records that pass schema validation.

    If *drop_invalid* is ``False``, invalid records are still yielded but
    a ``_validation_errors`` key is injected with the list of errors.
    """
    for record in records:
        errors = validate_record(record, schema)
        if not errors:
            yield record
        elif not drop_invalid:
            yield {**record, "_validation_errors": errors}
