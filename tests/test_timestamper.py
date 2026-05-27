"""Tests for logslice.timestamper."""

from __future__ import annotations

import pytest
from logslice.timestamper import normalise_timestamp, convert_to_epoch


def _records(*items):
    return list(items)


# ---------------------------------------------------------------------------
# normalise_timestamp
# ---------------------------------------------------------------------------

def test_normalise_adds_dst_field():
    rec = {"timestamp": 0}
    result = list(normalise_timestamp([rec]))
    assert "time" in result[0]


def test_normalise_epoch_zero_is_unix_epoch():
    rec = {"timestamp": 0}
    result = list(normalise_timestamp([rec]))
    assert result[0]["time"] == "1970-01-01T00:00:00Z"


def test_normalise_milliseconds_unit():
    rec = {"timestamp": 1_000}
    result = list(normalise_timestamp([rec], unit="ms"))
    assert result[0]["time"] == "1970-01-01T00:00:01Z"


def test_normalise_missing_field_passes_through():
    rec = {"level": "info"}
    result = list(normalise_timestamp([rec]))
    assert result[0] == {"level": "info"}
    assert "time" not in result[0]


def test_normalise_non_numeric_field_passes_through():
    rec = {"timestamp": "not-a-number"}
    result = list(normalise_timestamp([rec]))
    assert "time" not in result[0]


def test_normalise_custom_src_and_dst_fields():
    rec = {"ts": 0}
    result = list(normalise_timestamp([rec], src_field="ts", dst_field="iso"))
    assert "iso" in result[0]
    assert "time" not in result[0]


def test_normalise_custom_format():
    rec = {"timestamp": 0}
    result = list(normalise_timestamp([rec], fmt="%Y/%m/%d"))
    assert result[0]["time"] == "1970/01/01"


def test_normalise_original_fields_preserved():
    rec = {"timestamp": 0, "level": "warn", "msg": "hi"}
    result = list(normalise_timestamp([rec]))
    assert result[0]["level"] == "warn"
    assert result[0]["msg"] == "hi"


# ---------------------------------------------------------------------------
# convert_to_epoch
# ---------------------------------------------------------------------------

def test_convert_to_epoch_basic():
    rec = {"time": "1970-01-01T00:00:00Z"}
    result = list(convert_to_epoch([rec]))
    assert result[0]["epoch"] == pytest.approx(0.0)


def test_convert_to_epoch_missing_field_passes_through():
    rec = {"level": "info"}
    result = list(convert_to_epoch([rec]))
    assert "epoch" not in result[0]


def test_convert_to_epoch_non_string_passes_through():
    rec = {"time": 12345}
    result = list(convert_to_epoch([rec]))
    assert "epoch" not in result[0]


def test_convert_to_epoch_invalid_format_passes_through():
    rec = {"time": "not-a-date"}
    result = list(convert_to_epoch([rec]))
    assert "epoch" not in result[0]


def test_convert_to_epoch_custom_fields():
    rec = {"ts_str": "1970-01-01T00:00:01Z"}
    result = list(convert_to_epoch([rec], src_field="ts_str", dst_field="ts_epoch"))
    assert result[0]["ts_epoch"] == pytest.approx(1.0)


def test_convert_preserves_other_fields():
    rec = {"time": "1970-01-01T00:00:00Z", "msg": "hello"}
    result = list(convert_to_epoch([rec]))
    assert result[0]["msg"] == "hello"
