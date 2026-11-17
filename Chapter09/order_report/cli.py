"""Run the file-exchange workshop without changing input data."""
from pathlib import Path
import sys
import tempfile

from .file_io import (
    read_orders_csv, read_orders_json, write_orders_csv,
    write_orders_json,
)
from .reporting import build_report, format_report

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Compare the two inputs; run exports in a disposable directory."""
    csv_rows = read_orders_csv(ROOT / "data" / "orders.csv")
    json_rows = read_orders_json(ROOT / "data" / "orders.json")
    if csv_rows != json_rows:
        raise ValueError("CSV and JSON inputs differ")
    report_text = format_report(build_report(csv_rows))
    with tempfile.TemporaryDirectory(prefix="chapter09-workshop-") as folder:
        output = Path(folder)
        write_orders_csv(csv_rows, output / "orders.csv")
        write_orders_json(csv_rows, output / "orders.json")
        if read_orders_csv(output / "orders.csv") != csv_rows:
            raise ValueError("CSV round trip failed")
        if read_orders_json(output / "orders.json") != csv_rows:
            raise ValueError("JSON round trip failed")
        with (output / "report.txt").open("x", encoding="utf-8",
                                          newline="\n") as target:
            target.write(report_text + "\n")
    print(report_text)
    print("csv_json_equal True")
    print("round_trip_equal True")
    print("temporary_exports_removed True")


if __name__ == "__main__":
    main()
