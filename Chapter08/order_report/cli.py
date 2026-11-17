"""Keep console output at the application boundary."""
from .reporting import build_report, format_report
from .sample_data import make_orders


def main() -> None:
    """Build the synthetic report and print it once."""
    report = build_report(make_orders())
    print(format_report(report))


if __name__ == "__main__":
    main()
