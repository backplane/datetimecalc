Module datetimecalc.functions
=============================
functions for working with simple temporal expressions

Functions
---------


`is_datetime(obj: Any) ‑> bool`
:   Check if the given object is a datetime.

    Args:
        obj: The object to be checked.

    Returns:
        True if the object is a datetime, False otherwise.

    Examples:
        >>> is_datetime(datetime.now())
        True

        >>> is_datetime(timedelta(days=1))
        False


`is_timedelta(obj: Any) ‑> bool`
:   Check if the given object is a timedelta.

    Args:
        obj: The object to be checked.

    Returns:
        True if the object is a timedelta, False otherwise.

    Examples:
        >>> is_timedelta(timedelta(days=1))
        True

        >>> is_timedelta(datetime.now())
        False


`parse_datetime_str(input_str: str) ‑> datetime.datetime`
:   Parse the input string for a natural language reference to a date and
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


`parse_temporal_expr(expression: str) ‑> Union[datetime.datetime, datetime.timedelta]`
:   Parse a temporal expression and perform the corresponding operation.

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


`parse_temporal_str(input_str: str) ‑> Union[datetime.datetime, datetime.timedelta]`
:   Parse a string as either a datetime or a timedelta.

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


`parse_timedelta_str(input_str: str) ‑> datetime.timedelta`
:   Parses a string containing time delta information and returns a timedelta object

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
