"""Read and export the small, explicitly defined order dataset.

Readers load the complete dataset in memory. Writers validate first, then
open with mode 'x' unless overwrite=True. Writes are not transactional.
"""
import csv
from datetime import date
import json
from pathlib import Path

FIELDS = (
    "order_id", "order_date", "category", "quantity",
    "unit_price_toman", "returned_quantity",
)
INTEGER_FIELDS = ("quantity", "unit_price_toman", "returned_quantity")


def validate_orders(rows: list[dict]) -> None:
    """Check this chapter's schema without editing the input.

    Require a list of exact-schema dictionaries, unique nonblank string
    IDs, canonical ISO calendar dates, nonblank string categories, and
    valid integer amounts. Leading/trailing text whitespace is rejected.
    Booleans and floating-point values are not integers for this schema.
    Empty lists are allowed. This is not a general validation framework.
    """
    if not isinstance(rows, list):
        raise ValueError("Orders must be a list")
    seen = set()
    for index, row in enumerate(rows, start=1):
        label = f"Record {index}"
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f"{label}: unexpected fields")
        for field in ("order_id", "order_date", "category"):
            value = row[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label}: {field} must be nonblank text")
            if value != value.strip():
                raise ValueError(f"{label}: {field} has outer whitespace")
        parsed_date = date.fromisoformat(row["order_date"])
        if parsed_date.isoformat() != row["order_date"]:
            raise ValueError(f"{label}: use YYYY-MM-DD dates")
        for field in INTEGER_FIELDS:
            if type(row[field]) is not int:
                raise ValueError(f"{label}: {field} must be an integer")
        if row["quantity"] <= 0 or row["unit_price_toman"] < 0:
            raise ValueError(f"{label}: invalid quantity or price")
        if not 0 <= row["returned_quantity"] <= row["quantity"]:
            raise ValueError(f"{label}: invalid returned quantity")
        if row["order_id"] in seen:
            raise ValueError(f"{label}: duplicate order_id")
        seen.add(row["order_id"])


def read_orders_csv(path: str | Path) -> list[dict]:
    """Read comma-delimited UTF-8 CSV, optionally with an initial BOM.

    Header order must exactly match FIELDS. Integer cells use int();
    numeric whitespace and explicit signs accepted by int() are allowed.
    Completely blank physical lines are skipped by csv.DictReader.
    Error record numbers are logical records, not physical line numbers.
    """
    rows = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames != list(FIELDS):
            raise ValueError("CSV header must match FIELDS in order")
        for index, row in enumerate(reader, start=1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Record {index}: wrong field count")
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    validate_orders(rows)
    return rows


def read_orders_json(path: str | Path) -> list[dict]:
    """Parse one UTF-8 JSON document, then check the order schema.

    An initial BOM is accepted by the text decoder. Repeated JSON object
    keys follow json.load defaults: only the last value remains visible.
    """
    with Path(path).open("r", encoding="utf-8-sig") as source:
        rows = json.load(source)
    validate_orders(rows)
    return rows


def write_orders_csv(rows: list[dict], path: str | Path, *,
                     overwrite: bool = False) -> None:
    """Export validated orders; do not create parent directories."""
    validate_orders(rows)
    mode = "w" if overwrite else "x"
    with Path(path).open(mode, encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS,
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_orders_json(rows: list[dict], path: str | Path, *,
                      overwrite: bool = False) -> None:
    """Export one JSON array; no append mode and no parent creation."""
    validate_orders(rows)
    mode = "w" if overwrite else "x"
    with Path(path).open(mode, encoding="utf-8", newline="\n") as target:
        json.dump(rows, target, ensure_ascii=True, indent=2,
                  allow_nan=False)
        target.write("\n")
