"""Read CSV lazily and translate expected syntax failures with context."""
import csv
from pathlib import Path
from .errors import DataContractError
from .validation import FIELDS, INTEGER_FIELDS


def iter_orders_csv(path):
    """Own the file until exhausted or explicitly closed by the caller.

    Record numbers count logical data records, excluding the header.
    Integer conversion accepts the syntax supported by int().
    """
    record_number = 0
    with Path(path).open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            if reader.fieldnames != list(FIELDS):
                raise DataContractError("invalid_header")
            for record_number, row in enumerate(reader, start=1):
                if None in row or any(value is None for value in row.values()):
                    raise DataContractError("wrong_field_count", record_number)
                for field in INTEGER_FIELDS:
                    try:
                        row[field] = int(row[field])
                    except ValueError as exc:
                        raise DataContractError(
                            "invalid_integer", record_number, field
                        ) from exc
                yield row
        except csv.Error as exc:
            raise DataContractError("invalid_csv") from exc
        except UnicodeError as exc:
            raise DataContractError("invalid_encoding") from exc
