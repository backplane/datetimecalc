#!/usr/bin/env python3
"""
Command-line interface for datetimecalc.

Usage:
    datetimecalc "2024-01-01 + 1 week"
    datetimecalc "tomorrow - 2 hours"
    datetimecalc "2025-01-01 - 2024-01-01"
    datetimecalc --repr "1 day + 12 hours"
    datetimecalc --debug "now @ UTC"
"""

import argparse
import logging
import sys
from importlib.metadata import version

from .functions import format_temporal_object, parse_temporal_expr


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with
    sys.exit
    """
    argp = argparse.ArgumentParser(
        prog=__package__,
        description=(
            "program which parses natural language datetime and timedelta expressions"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argp.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version(__package__)}",
    )
    argp.add_argument(
        "--debug",
        action="store_true",
        help="enable debug output",
    )
    argp.add_argument(
        "--repr",
        action="store_true",
        help="use the python repr function on the object instead of "
        "human-friendly formatting",
    )
    argp.add_argument(
        "expr",
        nargs="+",
        help="a natural language date and time operation expression",
    )
    args = argp.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if args.debug else logging.WARNING,
    )

    obj = parse_temporal_expr(" ".join(args.expr))
    print(repr(obj) if args.repr else format_temporal_object(obj))

    return 0


if __name__ == "__main__":
    sys.exit(main())
