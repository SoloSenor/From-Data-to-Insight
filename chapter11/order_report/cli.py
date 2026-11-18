"""Catch expected input failures only at the application boundary."""
import argparse
from pathlib import Path
import sys
from .errors import DataContractError
from .pipeline import format_report
from .service import run_report

DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data/orders.csv"


def main(argv=None, stdout=None, stderr=None):
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    parser = argparse.ArgumentParser(description="Validate and summarize orders")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = run_report(args.path)
    except DataContractError as exc:
        if args.debug:
            raise
        print(f"ERROR data: {exc}", file=stderr)
        return 3
    except OSError:
        if args.debug:
            raise
        print("ERROR io: cannot read input file", file=stderr)
        return 2
    print(format_report(report), file=stdout)
    return 0
