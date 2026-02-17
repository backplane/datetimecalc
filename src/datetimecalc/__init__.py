"""
Natural language datetime and timedelta calculator.

This library provides functions for parsing and computing with datetime and
timedelta expressions using natural language syntax.

Example usage::

    from datetimecalc import parse_temporal_expr

    parse_temporal_expr('2024-01-01 00:00 + 1 week')
    # datetime.datetime(2024, 1, 8, 0, 0)

    parse_temporal_expr('2025-01-01 - 2024-01-01')
    # datetime.timedelta(days=366)

    parse_temporal_expr('1 day == 24 hours')
    # True

Main functions:
    parse_temporal_expr: Parse and evaluate expressions like "2024-01-01 + 1 day"
    parse_datetime_str: Parse natural language dates like "tomorrow at 3pm"
    parse_timedelta_str: Parse durations like "1 day 2 hours"
    parse_temporal_str: Parse either datetime or timedelta strings
"""

from .functions import (
    is_datetime,
    is_timedelta,
    parse_datetime_str,
    parse_temporal_expr,
    parse_temporal_str,
    parse_timedelta_str,
)

__all__ = (
    "is_datetime",
    "is_timedelta",
    "parse_datetime_str",
    "parse_temporal_expr",
    "parse_temporal_str",
    "parse_timedelta_str",
)
