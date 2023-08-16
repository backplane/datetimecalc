Module datetimecalc.tz
======================
helper functions for working with timezones

Functions
---------


`bounded_capture_join(items: List[str]) ‑> str`
:   Concatenates a list of strings into a single string, using a capturing
    group in regex.

    Args:
        items: List of strings to be joined.

    Returns:
        The joined string with capturing group.

    Examples:
        >>> bounded_capture_join(['a', 'b', 'c']) == r'\b(a|b|c)\b'
        True


`gen_tz_regex() ‑> re.Pattern`
:   Generates a regular expression pattern for matching timezone strings.

    Returns:
        Compiled regular expression pattern for matching timezone abbreviations.

    Examples:
        >>> pattern = gen_tz_regex()
        >>> pattern.match('CEST')
        <re.Match object; span=(0, 4), match='CEST'>


`noncapture_join(items: List[str]) ‑> str`
:   Concatenates a list of strings into a single string, using a non-capturing
    group in regex.

    Args:
        items: List of strings to be joined.

    Returns:
        The joined string with non-capturing group.

    Examples:
        >>> noncapture_join(['a', 'b', 'c'])
        '(?:a|b|c)'


`search_tz(input_date: str) ‑> Optional[datetime.tzinfo]`
:   Searches for a timezone name in an input date string and returns the
    corresponding ZoneInfo object.

    Args:
        input_date: A string representing a date with a timezone in it.

    Returns:
        The ZoneInfo object corresponding to the timezone if found, else None.

    Examples:
        >>> search_tz("Sun 13 Aug 2023 09:08:52 AM CEST")
        zoneinfo.ZoneInfo(key='Europe/Brussels')

        >>> search_tz("Sun 13 Aug 2023 09:08:52 AM EST")
        zoneinfo.ZoneInfo(key='EST')
