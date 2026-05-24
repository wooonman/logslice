"""Terminal colour highlighting for log output."""

from __future__ import annotations

import re
from typing import Any

# ANSI escape codes
_RESET = "\033[0m"
_BOLD = "\033[1m"

_LEVEL_COLOURS: dict[str, str] = {
    "debug": "\033[36m",    # cyan
    "info": "\033[32m",     # green
    "warn": "\033[33m",     # yellow
    "warning": "\033[33m",  # yellow
    "error": "\033[31m",    # red
    "critical": "\033[35m", # magenta
    "fatal": "\033[35m",    # magenta
}

_KEY_COLOUR = "\033[34m"   # blue
_STR_COLOUR = "\033[32m"   # green
_NUM_COLOUR = "\033[33m"   # yellow
_BOOL_COLOUR = "\033[35m"  # magenta
_NULL_COLOUR = "\033[90m"  # dark grey


def colourise_level(level: str) -> str:
    """Return *level* wrapped in the appropriate ANSI colour codes."""
    colour = _LEVEL_COLOURS.get(level.lower(), "")
    if colour:
        return f"{colour}{_BOLD}{level.upper()}{_RESET}"
    return level.upper()


def colourise_json(text: str) -> str:
    """Apply syntax highlighting to a JSON string."""

    def _replace(m: re.Match[str]) -> str:  # type: ignore[type-arg]
        key = m.group(1)
        value = m.group(2)
        coloured_key = f'{_KEY_COLOUR}"{key}"{_RESET}'
        if value.startswith('"'):
            coloured_val = f"{_STR_COLOUR}{value}{_RESET}"
        elif value in ("true", "false"):
            coloured_val = f"{_BOOL_COLOUR}{value}{_RESET}"
        elif value == "null":
            coloured_val = f"{_NULL_COLOUR}{value}{_RESET}"
        else:
            coloured_val = f"{_NUM_COLOUR}{value}{_RESET}"
        return f"{coloured_key}: {coloured_val}"

    pattern = r'"([^"]+)":\s*("(?:[^"\\]|\\.)*"|true|false|null|-?\d+(?:\.\d+)?)'
    return re.sub(pattern, _replace, text)


def highlight_record(line: str, use_colour: bool = True) -> str:
    """Optionally apply colour highlighting to a formatted log line."""
    if not use_colour:
        return line
    return colourise_json(line)
