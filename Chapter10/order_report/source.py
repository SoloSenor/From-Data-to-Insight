"""CSV syntax and integer conversion; domain checks are in the accumulator."""
import csv
from pathlib import Path
from .validation import FIELDS, INTEGER_FIELDS


def iter_orders_csv(path: str | Path):
    """Yield parsed rows lazily. Own the file until exhaustion or close().

    This parser checks the header and field count, not the full domain schema.
    """
    with Path(path).open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames != list(FIELDS):
            raise ValueError("CSV header must match FIELDS in order")
        for index, row in enumerate(reader, start=1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Record {index}: wrong field count")
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            yield row
