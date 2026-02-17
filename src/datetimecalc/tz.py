#!/usr/bin/env python3
"""helper functions for working with timezones"""

__all__ = [
    "search_tz",
    "offset_timezone",
    "gen_tz_regex",
    "TZ_ADDITIONS",
]

import collections
import datetime
import os
import re
import time
import zoneinfo
from typing import Dict, Final, List, Optional, Tuple

# TZ_ADDITIONS contains the daylight saving time (DST) variants of the
# corresponding legacy short identifiers (these may be superseded by the local
# timezone if they match names in time.tzname) - for example BST could evaluate
# to Bangladesh Standard Time if the code is running in a Bangladesh timezone
TZ_ADDITIONS: Final[Dict[str, str]] = {
    # corresponding to European or commonwealth short timezone names
    "CEST": "Europe/Paris",  # Central European Summer Time - see also "CET"
    "EEST": "Europe/Athens",  # Eastern European Summer Time - see also "EET"
    "WEST": "Europe/Lisbon",  # Western European Summer Time - see also "WET"
    # corresponding to US short timezone names
    "EDT": "America/New_York",  # Eastern Daylight Time - see also "EST"
    "HDT": "Pacific/Honolulu",  # Hawaii Daylight Time - see also "HST"
    "MDT": "America/Denver",  # Mountain Daylight Time - see also "MST"
    # corresponding to grandfathered short timezone names
    "BST": "Europe/London",  # British Summer Time - see also "GB"
    "MEST": "Europe/Berlin",  # Middle European Summer Time - see also "MET"
    "NZDT": "Pacific/Auckland",  # New Zealand Daylight Time - see also "NZ"
}

# OFFSET_REGEX should match all time offsets from -12:00 to +14:00 in 15-minute
# increments, and only when they are immediately preceded by a digit or
# whitespace
OFFSET_REGEX: Final = r"(?:(?<=[\d\s])|^)([+-](?:0[0-9]|1[0-4]):(?:00|15|30|45))"


def offset_timezone(spec: str) -> datetime.timezone:
    """
    Accepts spec strings like "-05:00", "-04:00", "+05:30" that specify a
    timezone based on an offset in hours and minutes east from UTC; returns
    a datetime.timezone.

    :param spec: string representing an offset from UTC; format is +/-HH:MM
    :return: datetime.timezone object representing the specified timezone.

    >>> offset_timezone('-05:00')
    datetime.timezone(datetime.timedelta(days=-1, seconds=68400))
    >>> offset_timezone('+05:30')
    datetime.timezone(datetime.timedelta(seconds=19800))
    """
    # sanity-check
    if not (spec[0] in "+-" and len(spec) == 6 and spec.index(":") == 3):
        raise ValueError(
            f'Input "{spec}" is not a valid UTC offset string. '
            "Must be in the format +/-HH:MM."
        )

    # split and parse
    sign, hours, minutes = spec[0], int(spec[1:3]), int(spec[4:])

    # make the timedelta
    offset_in_minutes = hours * 60 + minutes
    if sign == "-":
        offset_in_minutes = -offset_in_minutes
    return datetime.timezone(datetime.timedelta(minutes=offset_in_minutes))


def delspan(string: str, span: Tuple[int, int]) -> str:
    """
    Deletes a span from a string.

    Args:
        string (str): The input string.
        span (Tuple[int, int]): A tuple of two integers indicating the beginning
                                and end of the span to be deleted.

    Returns:
        str: The string with the specified span deleted.

    Raises:
        TypeError: If the span is not a tuple of two integers.
        ValueError: If the span is out of range for the string.

    Examples:
        >>> delspan("Hello, world!", (7, 12))
        'Hello, !'
    """
    begin, end = span

    # pylint: disable=superfluous-parens
    if not (0 <= begin <= end <= len(string)):
        raise ValueError("Span is out of range for the string.")

    return string[:begin] + string[end:]


def noncapture_join(items: List[str]) -> str:
    """
    Concatenates a list of strings into a single string, using a non-capturing
    group in regex.

    Args:
        items: List of strings to be joined.

    Returns:
        The joined string with non-capturing group.

    Examples:
        >>> noncapture_join(['a', 'b', 'c'])
        '(?:a|b|c)'
    """
    return rf"(?:{'|'.join(sorted(items))})"


def bounded_capture_join(items: List[str]) -> str:
    """
    Concatenates a list of strings into a single string, using a capturing
    group in regex.

    Args:
        items: List of strings to be joined.

    Returns:
        The joined string with capturing group.

    Examples:
        >>> bounded_capture_join(['a', 'b', 'c']) == r'\\b(a|b|c)\\b'
        True
    """
    return rf"\b({'|'.join(sorted(items))})\b"


def gen_tz_regex() -> re.Pattern:
    """
    Generates a regular expression pattern for matching timezone strings.

    Returns:
        Compiled regular expression pattern for matching timezone abbreviations.

    Examples:
        >>> pattern = gen_tz_regex()
        >>> pattern.match('CEST')
        <re.Match object; span=(0, 4), match='CEST'>
    """
    grouped_tzs = collections.defaultdict(list)
    for tzname in zoneinfo.available_timezones():
        slashidx = tzname.find("/")
        if slashidx == -1:
            grouped_tzs["ROOT"].append(tzname)
            continue
        grouped_tzs[tzname[0:slashidx]].append(tzname[slashidx + 1 :])

    tz_regex_parts = grouped_tzs.pop("ROOT")
    tz_regex_parts.extend(
        [
            f"{region}/{noncapture_join(subregions)}"
            for region, subregions in grouped_tzs.items()
        ]
    )
    tz_regex_parts.extend(TZ_ADDITIONS.keys())
    tz_regex_parts.extend(time.tzname)

    return re.compile(
        noncapture_join(
            [
                OFFSET_REGEX,
                bounded_capture_join(tz_regex_parts),
            ]
        )
    )


tz_regex = gen_tz_regex()


# pylint: disable=too-many-return-statements
def search_tz(
    input_date: str, fullmatch: bool = False
) -> Tuple[Optional[datetime.tzinfo], Optional[str]]:
    """
    Searches for a timezone name in an input date string and returns the
    corresponding ZoneInfo object. If 'fullmatch' is True, the entire input_date
    string must be a timezone name.

    Args:
        input_date: A string representing a date with a timezone in it.
        fullmatch: Indicates that the search must match the entire input_date string.

    Returns:
        The ZoneInfo object corresponding to the timezone if found, else None.
        The input_date with any matched timezone deleted, else None

    Examples:
        >>> search_tz("Sun 13 Aug 2023 09:08:52 AM CEST")
        (zoneinfo.ZoneInfo(key='Europe/Brussels'), 'Sun 13 Aug 2023 09:08:52 AM ')

        >>> search_tz("Sun 13 Aug 2023 09:08:52 AM EST")
        (zoneinfo.ZoneInfo(key='EST'), 'Sun 13 Aug 2023 09:08:52 AM ')
    """
    search_func = tz_regex.fullmatch if fullmatch else tz_regex.search
    match = search_func(input_date)
    if not match:
        return None, None
    name = match.group(1) if match.group(1) else match.group(2)
    filtered_input = delspan(input_date, match.span())

    # Check if the name is actually an offset
    try:
        return offset_timezone(name), filtered_input
    except ValueError:
        pass

    try:
        return zoneinfo.ZoneInfo(name), filtered_input
    except zoneinfo.ZoneInfoNotFoundError:
        pass

    # Check if name matches the local timezone abbreviations
    if name in time.tzname:
        # If we have a TZ envvar set, we use the ZoneInfo matching that
        if tz_env := os.environ.get("TZ"):
            return zoneinfo.ZoneInfo(tz_env), filtered_input

        # Return a ZoneInfo based on UTC offset
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=utc_offset_sec)
        return datetime.timezone(utc_offset), filtered_input

    try:
        return zoneinfo.ZoneInfo(TZ_ADDITIONS[name]), filtered_input
    except zoneinfo.ZoneInfoNotFoundError:
        pass
    except KeyError:
        pass

    return None, None
