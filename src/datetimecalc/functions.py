"""functions for working with simple temporal expressions"""

import logging
import operator
import re
from datetime import datetime, timedelta, timezone, tzinfo
from typing import (
    Any,
    Callable,
    Container,
    Dict,
    Final,
    Optional,
    Sequence,
    Tuple,
    TypeAlias,
    Union,
)

import parsedatetime

from .timedelta import duration_to_string
from .tz import search_tz

TemporalObject: TypeAlias = Union[datetime, timedelta, tzinfo]


def spliton(seq: Sequence[Any], **kwargs) -> Tuple[Sequence[Any], Sequence[Any]]:
    """
    Splits a sequence into two sequences based on the first item matching a
    condition.

    Args:
        seq (Sequence): The sequence to be split.
        **kwargs: A single keyword argument specifying the predicate and the
          comparison value. The keyword must be one of the following strings:
          'lt', 'le', 'eq', 'ne', 'ge', 'gt', 'is_', 'is_not', 'contains',
          'isin', 'notin'.
          The value is the second term in the binary predicate operation.

    Returns:
        Tuple[Sequence, Sequence]: A tuple of two sequences: the first contains
          items up to the first item matching the condition, the second
          contains the first item matching the condition and all items after
          it.

    Raises:
        TypeError: If the number of keyword arguments is not 1, or if the predicate
                   keyword is not supported.

    Examples:
        >>> spliton([1, 2, 3, 4, 5], gt=3)
        ([1, 2, 3], [4, 5])
    """
    # quick sanity check
    if len(kwargs) != 1:
        raise TypeError("a predicate keyword argument must be specified")

    def isin(item: Any, container: Container) -> bool:
        return item in container

    def notin(item: Any, container: Container) -> bool:
        return item not in container

    predicates: Final[Dict[str, Callable[[Any, Any], bool]]] = {
        "lt": operator.lt,
        "le": operator.le,
        "eq": operator.eq,
        "ne": operator.ne,
        "ge": operator.ge,
        "gt": operator.gt,
        "is_": operator.is_,
        "is_not": operator.is_not,
        "contains": operator.contains,
        "isin": isin,
        "notin": notin,
    }
    predicate_name, b_term = next(iter(kwargs.items()))
    try:
        predicate_func = predicates[predicate_name]
    except KeyError:
        raise TypeError(f'unsupported predicate: "{predicate_name}"') from None

    # finally we enumerate the sequence looking for the first hit
    for i, a_term in enumerate(seq):
        if predicate_func(a_term, b_term):
            return seq[:i], seq[i:]

    # return the whole sequence and an empty sequence if no item matches the
    # condition
    return (seq, type(seq)())


def parse_timezone_str(input_str: str) -> tzinfo:
    """
    Parse the input string for a natural language reference to a timezone and
    return the corresponding tzinfo

    Args:
        input_str: The input string containing the natural language reference.

    Returns:
        A tzinfo object representing the parsed timezone string.

    Raises:
        ValueError: If the input string cannot be parsed.

    """
    tz_result, _ = search_tz(input_str, fullmatch=True)
    if tz_result:
        return tz_result
    raise ValueError("Invalid timezone string")


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
    tzinfo_obj, filtered_input = search_tz(input_str)
    if tzinfo_obj:
        logging.debug(
            'recognized timezone "%s"; proceeding to parse: "%s"',
            str(tzinfo_obj),
            filtered_input,
        )
    else:
        logging.debug("no recognized timezone")

    # Create a parsedatetime.Calendar instance
    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    # Use parsedatetime.Calendar.parseDT to parse the input string and obtain a
    # datetime object
    parsed_date, parse_status = cal.parseDT(
        filtered_input if tzinfo_obj else input_str,
        tzinfo=tzinfo_obj,
        # sourceTime=datetime(1, 1, 1),
    )
    logging.debug("parsed_date: %s, accuracy: %s", parsed_date, parse_status.accuracy)
    if not parse_status or parse_status.accuracy == 0:
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


def parse_repr_str(repr_str: str) -> TemporalObject:
    """
    Parses the repr forms of datetime and timedelta objects and returns
    equivalent objects.

    Args:
        repr_str: A string in the repr format of a datetime, or timedelta, object.

    Returns:
        The datetime, timedelta, or tzinfo object represented by the input string.

    Raises:
        ValueError: If the input string cannot be parsed to any of these types.

    Examples:
        >>> parse_repr_str("datetime.datetime(2023, 8, 21, 14, 30, 45, 780000, "\
        "tzinfo=datetime.timezone.utc)")
        datetime.datetime(2023, 8, 21, 14, 30, 45, 780000, tzinfo=datetime.timezone.utc)
        >>> parse_repr_str("datetime.datetime(2023, 8, 21, 14, 30, 45, 780000)")
        datetime.datetime(2023, 8, 21, 14, 30, 45, 780000)
        >>> parse_repr_str("datetime.timedelta(seconds=86400)")
        datetime.timedelta(days=1)
        >>> parse_repr_str("datetime.timedelta(days=2, seconds=3600, "\
        "microseconds=500000)")
        datetime.timedelta(days=2, seconds=3600, microseconds=500000)
    """
    # Regular expressions to match repr strings
    datetime_repr = re.compile(
        r"\s*"
        r"datetime\.(?P<class>datetime|timedelta)\("
        r"(?P<arglist>"
        r"(?:"
        r"(?:(?:days|(?:micro)?seconds)=)?(?:\d+)(?:,\s)?)+"
        r"(?:tzinfo=.+?)?"
        r")"
        r"\)"
        r"\s*"
    )
    zoneinfo_repr = re.compile(r"zoneinfo.ZoneInfo\(key='(?P<key>.+?)'\)")

    match = datetime_repr.fullmatch(repr_str)
    if not match:
        raise ValueError("not a valid datetime repr")

    obj_class = match.group("class")
    arglist = match.group("arglist").split(", ")
    args, kwarg_strs = spliton(arglist, contains="=")
    logging.debug("obj_class: %s", repr(obj_class))
    logging.debug("arglist: %s", repr(arglist))
    logging.debug("args: %s", repr(args))
    logging.debug("kwargs: %s", repr(kwarg_strs))

    if obj_class == "datetime":
        tz_arg: Optional[tzinfo] = None
        for kwarg in kwarg_strs:
            k, valstr = kwarg.split("=", 2)
            if k != "tzinfo":
                raise ValueError(f"can't parse kwarg int datetime repr: {kwarg}")
            if valstr == "datetime.timezone.utc":
                tz_arg = timezone.utc
            if match := zoneinfo_repr.match(valstr):
                tz_arg = parse_timezone_str(match.group("key"))
        # https://github.com/python/mypy/issues/10348
        return datetime(*[int(arg) for arg in args[:7]], tzinfo=tz_arg)  # type: ignore

    if obj_class == "timedelta":
        return timedelta(
            **{
                k: int(v)
                for k, v in (kwarg_str.split("=", 2) for kwarg_str in kwarg_strs)
            }
        )

    raise ValueError(f"Cannot parse {repr_str!r} as datetime or timedelta")


def parse_temporal_str(input_str: str) -> TemporalObject:
    """
    Parse a string as a datetime, timedelta, or timezone

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
    logging.debug('trying "%s" as timezone', input_str)
    try:
        return parse_timezone_str(input_str)
    except ValueError:
        pass

    logging.debug('trying "%s" as timedelta', input_str)
    try:
        return parse_timedelta_str(input_str)
    except ValueError:
        pass

    logging.debug('trying "%s" as datetime', input_str)
    try:
        return parse_datetime_str(input_str)
    except ValueError:
        pass

    logging.debug("no matches found")
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


def is_timezone(obj: Any) -> bool:
    """
    Check if the given object is a tzinfo.

    Args:
        obj: The object to be checked.

    Returns:
        True if the object is a tzinfo, False otherwise.

    Examples:
        >>> from datetime import timezone
        >>> is_timezone(timezone.utc)
        True

        >>> is_timezone(datetime.now())
        False
    """
    return isinstance(obj, tzinfo)


def parse_temporal_expr(expression: str) -> TemporalObject:
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
        r"\s+(?P<op>\+|\-|<|<=|>|>=|==|\!=|@)\s+"
        r"(?P<b>.+?)"
        r"\s*$"
        # fmt: on
    )

    match = time_op.match(expression)
    if not match:
        logging.debug("no match on time_op, trying as temporal_str")
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
        "@": lambda dt, tz: dt.astimezone(tz),
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
    elif is_datetime(a_term) and is_timezone(b_term):
        if op_string in ("@",):
            return op_func(a_term, b_term)
    elif is_timedelta(a_term) and is_timedelta(b_term):
        return op_func(a_term, b_term)
    elif is_timezone(a_term) and is_timezone(b_term):
        if op_string in ("-", "<", "<=", ">", ">=", "==", "!="):
            if not (isinstance(a_term, tzinfo) and isinstance(b_term, tzinfo)):
                raise ValueError(
                    "can't compare timezones unless both operands are tzinfo instances"
                )
            now = datetime.utcnow()
            return op_func(a_term.utcoffset(now), b_term.utcoffset(now))

    raise ValueError(
        f"Unsupported operation: "
        f"{type(a_term).__name__} {op_string} {type(b_term).__name__}"
    )


def format_temporal_object(obj: TemporalObject) -> str:
    """
    prints a string representation of the given object - this may or may not
    use the object's built-in string representations
    """
    if isinstance(obj, bool):
        return "True" if obj else "False"
    if is_datetime(obj):
        assert isinstance(obj, datetime)  # nosec: for mypy's benefit
        return str(obj)
    if is_timedelta(obj):
        assert isinstance(obj, timedelta)  # nosec: for mypy's benefit
        return duration_to_string(obj)
    if is_timezone(obj):
        assert isinstance(obj, tzinfo)  # nosec: for mypy's benefit
        return str(obj)
    raise ValueError(f'no handler for object of type {type(obj)} with value "{obj}"')
