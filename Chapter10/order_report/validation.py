"""The educational schema retained from chapter 09."""
from datetime import date

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

