"""Tests for logslice.cli_alert."""

import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.cli_alert import build_alert_parser, run_alert, _parse_alert_spec


def _args(**kwargs):
    defaults = dict(sources=["-"], alerts=[], passthrough=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _fake_iter_sources(records):
    def _inner(_sources):
        return iter(records)
    return _inner


# --- _parse_alert_spec ---

def test_parse_alert_spec_name_query_threshold():
    alert = _parse_alert_spec("myalert:level=error:3")
    assert alert.name == "myalert"
    assert alert.threshold == 3


def test_parse_alert_spec_default_threshold():
    alert = _parse_alert_spec("err:level=error")
    assert alert.threshold == 1


def test_parse_alert_spec_invalid_raises():
    with pytest.raises(ValueError):
        _parse_alert_spec("onlyone")


# --- run_alert ---

def test_run_alert_no_alerts_returns_error():
    out, err = StringIO(), StringIO()
    code = run_alert(_args(), out=out, err=err)
    assert code == 1
    assert "alert" in err.getvalue()


def test_run_alert_bad_spec_returns_error():
    out, err = StringIO(), StringIO()
    code = run_alert(_args(alerts=["badspec"]), out=out, err=err)
    assert code == 1


def test_run_alert_fires_on_match():
    recs = [{"level": "error", "msg": "oops"}]
    out, err = StringIO(), StringIO()
    with patch("logslice.cli_alert.iter_sources", _fake_iter_sources(recs)):
        code = run_alert(_args(alerts=["err:level=error:1"]), out=out, err=err)
    assert code == 0
    output = out.getvalue().strip()
    assert output  # something was printed
    data = json.loads(output)
    assert data["alert"] == "err"


def test_run_alert_no_match_no_output():
    recs = [{"level": "info", "msg": "ok"}]
    out, err = StringIO(), StringIO()
    with patch("logslice.cli_alert.iter_sources", _fake_iter_sources(recs)):
        code = run_alert(_args(alerts=["err:level=error:1"]), out=out, err=err)
    assert code == 0
    assert out.getvalue() == ""


def test_run_alert_passthrough_prints_all_records():
    recs = [{"level": "info"}, {"level": "error"}]
    out, err = StringIO(), StringIO()
    with patch("logslice.cli_alert.iter_sources", _fake_iter_sources(recs)):
        run_alert(_args(alerts=["err:level=error:1"], passthrough=True), out=out, err=err)
    lines = [l for l in out.getvalue().splitlines() if l]
    # 2 passthrough + 1 alert line
    assert len(lines) == 3


# --- build_alert_parser ---

def test_build_alert_parser_returns_parser():
    parser = build_alert_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_alert_parser_defaults():
    parser = build_alert_parser()
    args = parser.parse_args([])
    assert args.sources == ["-"]
    assert args.alerts == []
    assert not args.passthrough
