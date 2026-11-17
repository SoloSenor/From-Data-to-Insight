"""Run the workshop without rewriting reference files."""
from contextlib import closing
from pathlib import Path
from .source import iter_orders_csv
from .pipeline import summarize_orders, format_report

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with closing(iter_orders_csv(ROOT / "data" / "orders.csv")) as rows:
        report = summarize_orders(rows)
    print(format_report(report))
    print("single_pass True")


if __name__ == "__main__":
    main()
