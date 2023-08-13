#!/usr/bin/env python3
""" utility """
import argparse
import logging
import sys

from .functions import parse_temporal_expr


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with
    sys.exit
    """
    argp = argparse.ArgumentParser(
        prog=__package__,
        description=(
            "program which parses natural language datetime and timedelta "
            "expressions"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argp.add_argument(
        "--debug",
        action="store_true",
        help="enable debug output",
    )
    argp.add_argument(
        "temporal_expr",
        nargs="+",
        help="a natural language date and time operation expression",
    )
    args = argp.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if args.debug else logging.WARNING,
    )

    for expr in args.temporal_expr:
        print(parse_temporal_expr(expr))

    return 0


if __name__ == "__main__":
    sys.exit(main())
