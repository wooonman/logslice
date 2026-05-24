"""Tests for logslice.enricher."""

from __future__ import annotations

import socket

import pytest

from logslice.enricher import (
    enrich_hostname,
    enrich_index,
    enrich_static,
    enrich_timestamp,
)


# --- enrich_timestamp ---

def test_enrich_timestamp_adds_iso_field():
    recs = [{"ts": 0}]
    out = list(enrich_timestamp(recs))
    assert "timestamp_iso" in out[0]
    assert out[0]["timestamp_iso"].endswith("Z")


def test_enrich_timestamp_ms_unit():
    recs = [{"ts": 1_000_000}]  # 1000 seconds in ms
    out = list(enrich_timestamp(recs, unit="ms"))
    assert "timestamp_iso" in out[0]


def test_enrich_timestamp_missing_field_unchanged():
    recs = [{"msg": "no ts here"}]
    out = list(enrich_timestamp(recs))
    assert out == recs


def test_enrich_timestamp_invalid_value_unchanged():
    recs = [{"ts": "not-a-number"}]
    out = list(enrich_timestamp(recs))
    assert "timestamp_iso" not in out[0]


def test_enrich_timestamp_custom_fields():
    recs = [{"epoch": 0}]
    out = list(enrich_timestamp(recs, source_field="epoch", dest_field="time_str"))
    assert "time_str" in out[0]


# --- enrich_hostname ---

def test_enrich_hostname_adds_field():
    recs = [{"msg": "hi"}]
    out = list(enrich_hostname(recs))
    assert out[0]["hostname"] == socket.gethostname()


def test_enrich_hostname_no_override_by_default():
    recs = [{"hostname": "custom-host"}]
    out = list(enrich_hostname(recs))
    assert out[0]["hostname"] == "custom-host"


def test_enrich_hostname_override_flag():
    recs = [{"hostname": "custom-host"}]
    out = list(enrich_hostname(recs, override=True))
    assert out[0]["hostname"] == socket.gethostname()


def test_enrich_hostname_custom_field():
    recs = [{"msg": "hi"}]
    out = list(enrich_hostname(recs, field="host"))
    assert "host" in out[0]


# --- enrich_static ---

def test_enrich_static_adds_keys():
    recs = [{"msg": "hi"}]
    out = list(enrich_static(recs, {"env": "prod", "app": "api"}))
    assert out[0]["env"] == "prod"
    assert out[0]["app"] == "api"


def test_enrich_static_no_override_by_default():
    recs = [{"env": "staging"}]
    out = list(enrich_static(recs, {"env": "prod"}))
    assert out[0]["env"] == "staging"


def test_enrich_static_override_flag():
    recs = [{"env": "staging"}]
    out = list(enrich_static(recs, {"env": "prod"}, override=True))
    assert out[0]["env"] == "prod"


def test_enrich_static_empty_extra():
    recs = [{"msg": "hi"}]
    out = list(enrich_static(recs, {}))
    assert out == recs


# --- enrich_index ---

def test_enrich_index_adds_sequential():
    recs = [{"a": 1}, {"a": 2}, {"a": 3}]
    out = list(enrich_index(recs))
    assert [r["_index"] for r in out] == [0, 1, 2]


def test_enrich_index_custom_start():
    recs = [{"a": 1}, {"a": 2}]
    out = list(enrich_index(recs, start=10))
    assert out[0]["_index"] == 10


def test_enrich_index_custom_field():
    recs = [{"a": 1}]
    out = list(enrich_index(recs, field="seq"))
    assert "seq" in out[0]


def test_enrich_index_empty_stream():
    out = list(enrich_index([]))
    assert out == []
