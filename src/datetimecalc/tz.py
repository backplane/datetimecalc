#!/usr/bin/env python3
""" helper functions for working with timezones """
import collections
import datetime
import os
import re
import time
import zoneinfo
from typing import Dict, List, Optional

# tz_additions contains the daylight saving time (DST) variants of the
# corresponding legacy short identifiers (these may be superseded by the local
# timezone if they match names in time.tzname) - for example BST could evaluate
# to Bangladesh Standard Time if the code is running in a Bangladesh timezone
tz_additions: Dict[str, str] = {
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
    return rf'(?:{"|".join(sorted(items))})'


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
    return rf'\b({"|".join(sorted(items))})\b'


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
    tz_regex_parts.extend(tz_additions.keys())
    tz_regex_parts.extend(time.tzname)

    return re.compile(bounded_capture_join(tz_regex_parts))


tz_regex = gen_tz_regex()


def search_tz(input_date: str, fullmatch: bool = False) -> Optional[datetime.tzinfo]:
    """
    Searches for a timezone name in an input date string and returns the
    corresponding ZoneInfo object. If 'fullmatch' is True, the entire input_date
    string must be a timezone name.

    Args:
        input_date: A string representing a date with a timezone in it.
        fullmatch: Indicates that the search must match the entire input_date string.

    Returns:
        The ZoneInfo object corresponding to the timezone if found, else None.

    Examples:
        >>> search_tz("Sun 13 Aug 2023 09:08:52 AM CEST")
        zoneinfo.ZoneInfo(key='Europe/Brussels')

        >>> search_tz("Sun 13 Aug 2023 09:08:52 AM EST")
        zoneinfo.ZoneInfo(key='EST')
    """
    search_func = tz_regex.fullmatch if fullmatch else tz_regex.search
    match = search_func(input_date)
    if not match:
        return None
    name = match.group(1)

    try:
        return zoneinfo.ZoneInfo(name)
    except zoneinfo.ZoneInfoNotFoundError:
        pass

    # Check if name matches the local timezone abbreviations
    if name in time.tzname:
        # If we have a TZ envvar set, we use the ZoneInfo matching that
        if tz_env := os.environ.get("TZ"):
            return zoneinfo.ZoneInfo(tz_env)

        # Return a ZoneInfo based on UTC offset
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=utc_offset_sec)
        return datetime.timezone(utc_offset)

    try:
        return zoneinfo.ZoneInfo(tz_additions[name])
    except zoneinfo.ZoneInfoNotFoundError:
        pass
    except KeyError:
        pass

    return None
