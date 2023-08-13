""" functions for working with simple temporal expressions """
import logging
import operator
import re
from datetime import datetime, timedelta
from typing import Any, Union

import parsedatetime

from .tz import search_tz


def parse_datetime_str(input_str: str) -> datetime:
    """
    Parse the input string for a natural language reference to a date and
    return a datetime object.

    Args:
        input_str: The input string containing the natural language reference.

    Returns:
        A datetime object representing the parsed date.

    Raises:
        ValueError: If the input string cannot be parsed.

    Examples:
        >>> parse_datetime_str('tomorrow')
        datetime.datetime(...)
        >>> parse_datetime_str('next week')
        datetime.datetime(...)
        >>> parse_datetime_str("jan 6th 2022 9:00 AM UTC")
        datetime.datetime(2022, 1, 6, 9, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        >>> parse_datetime_str("2022-01-01 00:00 UTC")
        datetime.datetime(2022, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
    """
    # scan for timezone
    tzinfo = search_tz(input_str)

    # Create a parsedatetime.Calendar instance
    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    # Use parsedatetime.Calendar.parseDT to parse the input string and obtain a
    # datetime object
    parsed_date, parse_status = cal.parseDT(
        input_str,
        tzinfo=tzinfo,
        # sourceTime=datetime(1, 1, 1),
    )

    if not parse_status:
        raise ValueError("Unable to parse the input string.")

    # Make the datetime object timezone aware
    # parsed_date = parsed_date.replace(tzinfo=dateutil.tz.gettz())

    # Return the datetime object
    return parsed_date


def parse_timedelta_str(input_str: str) -> timedelta:
    """
    Parses a string containing time delta information and returns a timedelta object

    Args:
        input_string: A string containing the time delta information.

    Returns:
        A timedelta object representing the parsed time delta.

    Raises:
        ValueError: If the input_string is not a valid time delta string.

    Examples:
        >>> parse_timedelta_str('1d')
        datetime.timedelta(days=1)
        >>> parse_timedelta_str('1 day')
        datetime.timedelta(days=1)
        >>> parse_timedelta_str('2h 30m')
        datetime.timedelta(seconds=9000)
        >>> parse_timedelta_str('1.5h')
        datetime.timedelta(seconds=5400)
        >>> parse_timedelta_str('500ms')
        datetime.timedelta(microseconds=500000)
        >>> parse_timedelta_str('1 day 6.5 hours, 10 min 33s 3 year')
        datetime.timedelta(days=1096, seconds=24033)
    """
    pattern = re.compile(
        # fmt: off
        r"^\s*"
        r"(\s*\b"
        r"("
        r"(?P<years>\d+(\.\d+)?)\s*y(ears?)?|"
        r"(?P<months>\d+(\.\d+)?)\s*mo(n(ths?)?)?|"
        r"(?P<weeks>\d+(\.\d+)?)\s*w((eek|k)s?)?|"
        r"(?P<days>\d+(\.\d+)?)\s*d(ays?)?|"
        r"(?P<hours>\d+(\.\d+)?)\s*h(rs?|ours?)?|"
        r"(?P<minutes>\d+(\.\d+)?)\s*m(in(ute)?s?)?|"
        r"(?P<seconds>\d+(\.\d+)?)\s*s(ec(ond)?s?)?|"
        r"(?P<microseconds>\d+(\.\d+)?)\s*(μs|us|microsec(ond)?s?)|"
        r"(?P<milliseconds>\d+(\.\d+)?)\s*(ms|msec|millisec(ond)?s?)"
        r")"
        r"[\s,]*\b)+"
        r"\s*$"
        # fmt: on
    )
    match = pattern.match(input_str)
    if not match:
        raise ValueError("Invalid time delta string")
    parsed = match.groupdict()

    def fget(key: str) -> float:
        """
        return the float value corresponding to the given key in the parsed
        dict
        """
        val = parsed.get(key, "0")
        if val is None:
            val = "0"
        return float(val)

    return timedelta(
        days=(fget("years") * 365)
        + (fget("months") * 30)
        + (fget("weeks") * 7)
        + fget("days"),
        hours=fget("hours"),
        minutes=fget("minutes"),
        seconds=fget("seconds"),
        microseconds=fget("microseconds"),
        milliseconds=fget("milliseconds"),
    )


def parse_temporal_str(input_str: str) -> Union[datetime, timedelta]:
    """
    Parse a string as either a datetime or a timedelta.

    Args:
        input_str: The input string to parse.

    Returns:
        A datetime object if the string represents a date, or a timedelta
        object if it represents a time delta.

    Raises:
        ValueError: If the input string cannot be parsed as either a datetime
        or a timedelta.

    Examples:
        >>> parse_temporal_str('1d')
        datetime.timedelta(...)
        >>> parse_temporal_str('tomorrow')
        datetime.datetime(...)
    """
    try:
        return parse_timedelta_str(input_str)
    except ValueError:
        pass

    try:
        return parse_datetime_str(input_str)
    except ValueError:
        pass

    raise ValueError(
        f'unable to parse "{input_str}" as either a datetime nor a timedelta'
    )


def is_datetime(obj: Any) -> bool:
    """
    Check if the given object is a datetime.

    Args:
        obj: The object to be checked.

    Returns:
        True if the object is a datetime, False otherwise.

    Examples:
        >>> is_datetime(datetime.now())
        True

        >>> is_datetime(timedelta(days=1))
        False
    """
    return isinstance(obj, datetime)


def is_timedelta(obj: Any) -> bool:
    """
    Check if the given object is a timedelta.

    Args:
        obj: The object to be checked.

    Returns:
        True if the object is a timedelta, False otherwise.

    Examples:
        >>> is_timedelta(timedelta(days=1))
        True

        >>> is_timedelta(datetime.now())
        False
    """
    return isinstance(obj, timedelta)


def parse_temporal_expr(expression: str) -> Union[datetime, timedelta]:
    """
    Parse a temporal expression and perform the corresponding operation.

    The temporal expression should be in the format "<term> <operator> <term>",
    where <term> can be either a datetime or a timedelta object, and <operator>
    can be one of the following: '+', '-', '<', '<=', '>', '>=', '==', '!='.

    Args:
        expression: The temporal expression to parse.

    Returns:
        The result of the operation, which can be a datetime or a timedelta
        object.

    Raises:
        ValueError: If the expression is invalid or if the operation is not
        supported.

    Examples:
        >>> parse_temporal_expr('2022-01-01 12:00 UTC  + 1 day')
        datetime.datetime(2022, 1, 2, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

        >>> parse_temporal_expr('2022-01-01 00:00 - 1 week')
        datetime.datetime(2021, 12, 25, 0, 0)

        >>> parse_temporal_expr('2022-01-01 UTC < 2023-01-01 UTC')
        True

        >>> parse_temporal_expr('1 day == 24 hours')
        True

        >>> parse_temporal_expr('2025-01-02 - 2023-01-01')
        datetime.timedelta(days=732)

        >>> parse_temporal_expr('2022-01-01 + 2023-01-01')  # Raises ValueError
        Traceback (most recent call last):
            ...
        ValueError: Unsupported operation: datetime + datetime
    """
    time_op = re.compile(
        # fmt: off
        r"^\s*"
        r"(?P<a>.+?)"
        r"\s+(?P<op>\+|\-|<|<=|>|>=|==|\!=)\s+"
        r"(?P<b>.+?)"
        r"\s*$"
        # fmt: on
    )

    match = time_op.match(expression)
    if not match:
        try:
            return parse_temporal_str(expression)
        except ValueError:
            raise ValueError("unable to parse the expression, generally") from None
    logging.debug("capture groups: %s", match.groupdict())
    a_term = parse_temporal_str(match.group("a").strip())
    b_term = parse_temporal_str(match.group("b").strip())
    op_string = match.group("op").strip()
    op_func = {
        "+": operator.add,
        "-": operator.sub,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "==": operator.eq,
        "!=": operator.ne,
    }[op_string]

    logging.debug("%s %s %s", repr(a_term), repr(op_string), repr(b_term))

    if is_datetime(a_term) and is_timedelta(b_term):
        # datetime +/- timedelta == datetime
        if op_string in ("+", "-"):
            return op_func(a_term, b_term)
    elif is_datetime(a_term) and is_datetime(b_term):
        # datetime - datetime == timedelta
        # ...and...
        # datetime cmp datetime == bool
        if op_string in ("-", "<", "<=", ">", ">=", "==", "!="):
            return op_func(a_term, b_term)
    elif is_timedelta(a_term) and is_timedelta(b_term):
        return op_func(a_term, b_term)

    raise ValueError(
        f"Unsupported operation: "
        f"{type(a_term).__name__} {op_string} {type(b_term).__name__}"
    )
