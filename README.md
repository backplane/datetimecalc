# datetimecalc

A Python library and command-line tool for parsing and computing with natural language datetime and timedelta expressions.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/backplane/datetimecalc)](LICENSE.txt)

## Features

- **Natural language datetime parsing** - Parse expressions like "tomorrow at 3pm" or "next Friday"
- **Flexible timedelta syntax** - Support for "1 day", "2h 30m", "1.5 hours", etc.
- **Timezone support** - Handles IANA timezones, UTC offsets, and timezone conversions
- **Arithmetic operations** - Add/subtract dates and durations with intuitive syntax
- **Comparison operators** - Compare dates, times, and timedeltas
- **Internationalization** - Output formatting in 11 languages
- **Python repr() support** - Parse and output Python datetime repr strings
- **Modern tooling** - Built with uv package manager for fast, reliable dependency management

## Installation

### With uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/backplane/datetimecalc.git
cd datetimecalc
uv sync
```

### With pip

```bash
pip install git+https://github.com/backplane/datetimecalc.git
```

### Requirements

- Python 3.12 or higher
- parsedatetime >= 2.6

## Usage

### As a Library

```python
from datetimecalc.functions import parse_temporal_expr

# Addition of a date and a time duration
result = parse_temporal_expr('2022-01-01 12:00 UTC + 1 day')
print(result)
# Output: 2022-01-02 12:00:00+00:00

# Subtraction of a week duration from a date
result = parse_temporal_expr('2022-01-01 00:00 - 1 week')
print(result)
# Output: 2021-12-25 00:00:00

# Comparing two dates
result = parse_temporal_expr('2022-01-01 UTC < 2023-01-01 UTC')
print(result)
# Output: True

# Checking equality of two time durations
result = parse_temporal_expr('1 day == 24 hours')
print(result)
# Output: True

# Subtracting two dates
result = parse_temporal_expr('2025-01-02 - 2023-01-01')
print(result)
# Output: 2 years, 1 day

# Timezone conversion with @ operator
result = parse_temporal_expr('2024-01-01 12:00 America/New_York @ UTC')
print(result)
# Output: 2024-01-01 17:00:00+00:00

# UTC offset timezone parsing
result = parse_temporal_expr('2024-01-01 +05:30')
print(result)
# Output: 2024-01-01 00:00:00+05:30

# Compare timezones by offset
result = parse_temporal_expr('America/New_York == EST')
print(result)
# Output: True
```

### As a Command-Line Tool

```bash
# Basic usage
datetimecalc "tomorrow + 2 hours"

# With debug output
datetimecalc --debug "2024-01-01 + 1 week"

# Output Python repr() format
datetimecalc --repr "2025-01-01 - 2024-01-01"
# Output: datetime.timedelta(days=365)

# Multi-word expressions
datetimecalc tomorrow at 3pm + 2 hours

# Timezone operations
datetimecalc "2024-01-01 America/New_York @ UTC"

# Compare dates
datetimecalc "2024-01-01 < 2025-01-01"
```

### Using with uv

```bash
# Run without installing
uv run datetimecalc "tomorrow + 1 day"

# Run tests
uv run pytest

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Supported Operations

| Operation            | Syntax                           | Example                   |
| -------------------- | -------------------------------- | ------------------------- |
| Addition             | `datetime + timedelta`           | `2024-01-01 + 1 day`      |
| Subtraction          | `datetime - timedelta`           | `tomorrow - 2 hours`      |
| Date difference      | `datetime - datetime`            | `2025-01-01 - 2024-01-01` |
| Timezone conversion  | `datetime @ timezone`            | `2024-01-01 EST @ UTC`    |
| Comparison           | `<`, `<=`, `>`, `>=`, `==`, `!=` | `1 day == 24 hours`       |
| Timedelta arithmetic | `timedelta +/- timedelta`        | `1 day + 12 hours`        |

## Supported Time Units

Timedeltas support various formats:

- **Years**: `1 year`, `2 years`, `3y`
- **Months**: `1 month`, `2 months`, `3mo`
- **Weeks**: `1 week`, `2 weeks`, `3w`
- **Days**: `1 day`, `2 days`, `3d`
- **Hours**: `1 hour`, `2 hours`, `3h`, `1.5 hours`
- **Minutes**: `1 minute`, `2 minutes`, `3m`, `30 min`
- **Seconds**: `1 second`, `2 seconds`, `3s`
- **Milliseconds**: `500ms`, `1 millisecond`
- **Microseconds**: `500us`, `1 microsecond`

## Internationalization

Output is automatically localized based on system locale. Supported languages:

- English (en)
- Spanish (es)
- Chinese (zh)
- Hindi (hi)
- Portuguese (pt)
- Bengali (bn)
- Russian (ru)
- Japanese (ja)
- Vietnamese (vi)
- Turkish (tr)
- Marathi (mr)

```python
from datetimecalc.timedelta import duration_to_string
from datetime import timedelta

# Automatically uses system locale
print(duration_to_string(timedelta(days=2, hours=3)))
# English: "2 days, 3 hours"
# Spanish: "2 días, 3 horas"
# Japanese: "2日、3時間"
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/backplane/datetimecalc.git
cd datetimecalc

# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates .venv automatically)
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests (includes doctests)
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest src/datetimecalc/functions.py::parse_temporal_expr

# Run only doctests
uv run pytest --doctest-modules src
```

### Code Quality

```bash
# Format code
uv run black src/

# Sort imports
uv run isort --profile black src/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/
uv run pylint src/

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Building

```bash
# Build wheel
uv build

# Build standalone executable with PyOxidizer
pyoxidizer build
```

## Project Structure

```
datetimecalc/
├── src/datetimecalc/
│   ├── __init__.py          # Public API exports
│   ├── __main__.py          # CLI entry point
│   ├── functions.py         # Core parsing and expression evaluation
│   ├── timedelta.py         # Human-readable timedelta formatting (i18n)
│   └── tz.py                # Timezone detection and parsing
├── docs/                    # API documentation
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lockfile
├── CLAUDE.md                # Guide for Claude Code
└── README.md                # This file
```

## Documentation

- [API Documentation](docs/index.md)
- [Functions Module](docs/functions.md)
- [Timezone Module](docs/tz.md)
- [Development Guide](CLAUDE.md) - For contributors and Claude Code instances

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.txt](LICENSE.txt) file for details.

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass (`uv run pytest`)
2. Code is formatted (`uv run black src/`)
3. Pre-commit hooks pass (`uv run pre-commit run --all-files`)
4. Type hints are added for new functions
5. Doctests are included for new functionality

## Acknowledgments

- Built with [parsedatetime](https://github.com/bear/parsedatetime) for natural language date parsing
- Package management by [uv](https://github.com/astral-sh/uv)
- Timezone data from Python's [zoneinfo](https://docs.python.org/3/library/zoneinfo.html)

## Status

This project is under active development. See the [releases page](https://github.com/backplane/datetimecalc/releases) for changelog and version history.
