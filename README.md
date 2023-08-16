# datetimecalc

calculator for datetimes and timedeltas

This library and command-line tool are a work in progress.

```
from datetimecalc.functions import parse_temporal_expr

# Addition of a date and a time duration
result = parse_temporal_expr('2022-01-01 12:00 UTC + 1 day')
print(result)
# Output: datetime.datetime(2022, 1, 2, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

# Subtraction of a week duration from a date
result = parse_temporal_expr('2022-01-01 00:00 - 1 week')
print(result)
# Output: datetime.datetime(2021, 12, 25, 0, 0)

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
# Output: datetime.timedelta(days=732)
```

 For more information, see [the api docs](docs/index.md)
