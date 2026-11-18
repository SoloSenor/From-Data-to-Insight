"""Validate one exact-schema record before changing report state."""
from datetime import date
from .errors import DataContractError

FIELDS = ("order_id", "order_date", "category", "quantity",
          "unit_price_toman", "returned_quantity")
INTEGER_FIELDS = ("quantity", "unit_price_toman", "returned_quantity")


def validate_order(row, record_number=None):
    """Check the educational schema, not the truth of a transaction."""
    if not isinstance(row, dict) or set(row) != set(FIELDS):
        raise DataContractError("unexpected_fields", record_number)
    for field in ("order_id", "order_date", "category"):
        value = row[field]
        if not isinstance(value, str) or not value.strip():
            raise DataContractError("nonblank_text_required", record_number, field)
        if value != value.strip():
            raise DataContractError("outer_whitespace", record_number, field)
    try:
        parsed = date.fromisoformat(row["order_date"])
    except ValueError as exc:
        raise DataContractError("invalid_date", record_number, "order_date") from exc
    if parsed.isoformat() != row["order_date"]:
        raise DataContractError("canonical_date_required", record_number, "order_date")
    for field in INTEGER_FIELDS:
        if type(row[field]) is not int:
            raise DataContractError("integer_required", record_number, field)
    if row["quantity"] <= 0:
        raise DataContractError("positive_quantity_required", record_number, "quantity")
    if row["unit_price_toman"] < 0:
        raise DataContractError(
            "nonnegative_price_required", record_number, "unit_price_toman"
        )
    if not 0 <= row["returned_quantity"] <= row["quantity"]:
        raise DataContractError(
            "invalid_returned_quantity", record_number, "returned_quantity"
        )
