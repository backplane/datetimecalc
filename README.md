# datetimecalc

A Python library and command-line tool for parsing and computing with natural language datetime and timedelta expressions.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/backplane/datetimecalc)](LICENSE.txt)

## Quick Start

```bash
# Install with uv (recommended)
uv pip install git+https://github.com/backplane/datetimecalc.git

# Or clone and run directly
git clone https://github.com/backplane/datetimecalc.git
cd datetimecalc
uv run datetimecalc "tomorrow + 2 hours"
```

```bash
# Example commands
datetimecalc "2024-01-01 + 1 week"
datetimecalc "now - 30 days"
datetimecalc "2025-01-01 - 2024-01-01"      # Output: 1 year
datetimecalc "2024-01-01 EST @ UTC"          # Timezone conversion
datetimecalc "1 day == 24 hours"             # Output: True
```

## Features

- **Natural language parsing** - "tomorrow at 3pm", "next Friday", "in 2 hours"
- **Flexible duration syntax** - "1 day", "2h 30m", "1.5 hours", "90 minutes"
- **Timezone support** - IANA timezones, UTC offsets, and conversions with `@`
- **Date arithmetic** - Add, subtract, and compare dates and durations
- **Localized output** - Formats durations in 11 languages based on system locale
- **Python repr() support** - Parse and output Python datetime repr strings

## Installation

### With uv (recommended)

```bash
uv pip install git+https://github.com/backplane/datetimecalc.git
```

### With pip

```bash
pip install git+https://github.com/backplane/datetimecalc.git
```

### From source

```bash
git clone https://github.com/backplane/datetimecalc.git
cd datetimecalc
uv sync
```

**Requirements:** Python 3.12+

## Usage

### Command Line

```bash
# Date arithmetic
datetimecalc "2024-01-01 + 1 day"
datetimecalc "tomorrow - 2 hours"
datetimecalc "now + 1 week"

# Date differences
datetimecalc "2025-01-01 - 2024-01-01"
# Output: 1 year

# Timezone conversion
datetimecalc "2024-01-01 12:00 America/New_York @ UTC"
# Output: 2024-01-01 17:00:00+00:00

# Comparisons
datetimecalc "1 day == 24 hours"    # True
datetimecalc "2024-01-01 < now"     # True/False depending on current date

# Debug mode
datetimecalc --debug "2024-01-01 + 1 week"

# Python repr output
datetimecalc --repr "2025-01-01 - 2024-01-01"
# Output: datetime.timedelta(days=365)

# Multi-word expressions (no quotes needed)
datetimecalc tomorrow at 3pm + 2 hours
```

### Python Library

```python
from datetimecalc.functions import parse_temporal_expr

# Date + duration
parse_temporal_expr('2022-01-01 12:00 UTC + 1 day')
# datetime(2022, 1, 2, 12, 0, tzinfo=timezone.utc)

# Date - duration
parse_temporal_expr('2022-01-01 - 1 week')
# datetime(2021, 12, 25, 0, 0)

# Date - date (returns timedelta)
parse_temporal_expr('2025-01-01 - 2024-01-01')
# timedelta(days=365)

# Timezone conversion
parse_temporal_expr('2024-01-01 12:00 America/New_York @ UTC')
# datetime(2024, 1, 1, 17, 0, tzinfo=timezone.utc)

# Comparisons
parse_temporal_expr('2024-01-01 < 2025-01-01')  # True
parse_temporal_expr('1 day == 24 hours')        # True
```

## Operations Reference

| Operation           | Syntax                           | Example                   |
| ------------------- | -------------------------------- | ------------------------- |
| Add duration        | `datetime + timedelta`           | `2024-01-01 + 1 day`      |
| Subtract duration   | `datetime - timedelta`           | `tomorrow - 2 hours`      |
| Date difference     | `datetime - datetime`            | `2025-01-01 - 2024-01-01` |
| Convert timezone    | `datetime @ timezone`            | `2024-01-01 EST @ UTC`    |
| Duration arithmetic | `timedelta +/- timedelta`        | `1 day + 12 hours`        |
| Comparisons         | `<`, `<=`, `>`, `>=`, `==`, `!=` | `1 day == 24 hours`       |

## Duration Units

| Unit         | Formats                                 |
| ------------ | --------------------------------------- |
| Years        | `1 year`, `2 years`, `3y`               |
| Months       | `1 month`, `2 months`, `3mo`            |
| Weeks        | `1 week`, `2 weeks`, `3w`               |
| Days         | `1 day`, `2 days`, `3d`                 |
| Hours        | `1 hour`, `2 hours`, `3h`, `1.5 hours`  |
| Minutes      | `1 minute`, `2 minutes`, `3m`, `30 min` |
| Seconds      | `1 second`, `2 seconds`, `3s`           |
| Milliseconds | `500ms`, `1 millisecond`                |
| Microseconds | `500us`, `1 microsecond`                |

**Note:** Years and months use fixed approximations (1 year = 365 days, 1 month = 30 days).

## Localization

Duration output automatically adapts to system locale:

```python
from datetimecalc.timedelta import duration_to_string
from datetime import timedelta

duration_to_string(timedelta(days=2, hours=3))
# English: "2 days, 3 hours"
# Spanish: "2 días, 3 horas"
# Japanese: "2日、3時間"
```

**Supported languages:** English, Spanish, Chinese, Hindi, Portuguese, Bengali, Russian, Japanese, Vietnamese, Turkish, Marathi

## Development

```bash
# Setup
git clone https://github.com/backplane/datetimecalc.git
cd datetimecalc
uv sync
uv run pre-commit install

# Run tests
uv run pytest
uv run pytest -v                    # verbose
uv run pytest --doctest-modules src # doctests only

# Code quality
uv run pre-commit run --all-files   # all checks
uv run black src/                   # format
uv run mypy src/                    # type check

# Build
uv build                            # wheel
pyoxidizer build                    # standalone executable
```

## Project Structure

```
datetimecalc/
├── src/datetimecalc/
│   ├── __init__.py      # Public API exports
│   ├── __main__.py      # CLI entry point
│   ├── functions.py     # Core parsing and expression evaluation
│   ├── timedelta.py     # Human-readable timedelta formatting (i18n)
│   └── tz.py            # Timezone detection and parsing
├── pyproject.toml       # Project configuration
├── uv.lock              # Dependency lockfile
└── README.md
```

## Documentation

- [API Documentation](https://backplane.github.io/datetimecalc/) - Full API reference
- [Development Guide](CLAUDE.md) - Contributing and architecture

## Contributing

1. All tests pass: `uv run pytest`
2. Code is formatted: `uv run black src/`
3. Pre-commit hooks pass: `uv run pre-commit run --all-files`
4. Type hints included for new functions
5. Doctests included for new functionality

## License

Apache License 2.0 - see [LICENSE.txt](LICENSE.txt)

## Acknowledgments

- [parsedatetime](https://github.com/bear/parsedatetime) - Natural language date parsing
- [uv](https://github.com/astral-sh/uv) - Package management
- [zoneinfo](https://docs.python.org/3/library/zoneinfo.html) - Timezone data
