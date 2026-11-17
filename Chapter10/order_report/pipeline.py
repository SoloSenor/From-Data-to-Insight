"""Single-pass aggregation with explicit validation and duplicate tracking."""
from collections import defaultdict
from .validation import validate_orders


class ReportAccumulator:
    """Own per-instance state; add valid records one at a time.

    Duplicate tracking costs O(n) identifiers; grouped totals cost O(k).
    This is not a concurrent or transactional accumulator.
    """
    def __init__(self):
        self._orders = 0
        self._gross = 0
        self._refund = 0
        self._seen = set()
        self._categories = defaultdict(int)

    def add(self, row: dict) -> None:
        """Validate before updating the state for this record."""
        validate_orders([row])
        order_id = row["order_id"]
        if order_id in self._seen:
            raise ValueError("Duplicate order_id")
        gross = row["quantity"] * row["unit_price_toman"]
        refund = row["returned_quantity"] * row["unit_price_toman"]
        self._seen.add(order_id)
        self._orders += 1
        self._gross += gross
        self._refund += refund
        self._categories[row["category"]] += gross - refund

    def snapshot(self) -> dict:
        """Return a fresh report; do not expose internal mutable containers."""
        retained = self._gross - self._refund
        categories = [
            {"category": category, "retained_toman": amount,
             "share": amount / retained if retained else None}
            for category, amount in self._categories.items()
        ]
        categories.sort(key=lambda row: (-row["retained_toman"], row["category"]))
        return {"orders": self._orders, "gross_toman": self._gross,
                "refund_toman": self._refund, "retained_toman": retained,
                "categories": categories}


def summarize_orders(rows) -> dict:
    """Consume one iterable once; return only after successful exhaustion.

    Resource ownership remains with the caller.
    """
    accumulator = ReportAccumulator()
    for row in rows:
        accumulator.add(row)
    return accumulator.snapshot()


def format_report(report: dict) -> str:
    """Format an already constructed report; retained amount is not profit."""
    lines = [f"{key} {report[key]}" for key in
             ("orders", "gross_toman", "refund_toman", "retained_toman")]
    for row in report["categories"]:
        share = "NA" if row["share"] is None else f"{row['share']:.2%}"
        lines.append(f"{row['category']} {row['retained_toman']} {share}")
    return "\n".join(lines)
