"""Single-pass calculations, followed by explicit consistency checks."""
from collections import defaultdict
from math import isclose, isfinite
from .errors import DataContractError, ReportInvariantError
from .validation import validate_order


class ReportAccumulator:
    """Track IDs in O(n) and categories in O(k); not transactional."""
    def __init__(self):
        self._orders = 0
        self._gross = 0
        self._refund = 0
        self._seen = set()
        self._categories = defaultdict(int)

    def add(self, row, record_number=None):
        validate_order(row, record_number)
        if row["order_id"] in self._seen:
            raise DataContractError("duplicate_order_id", record_number, "order_id")
        gross = row["quantity"] * row["unit_price_toman"]
        refund = row["returned_quantity"] * row["unit_price_toman"]
        self._seen.add(row["order_id"])
        self._orders += 1
        self._gross += gross
        self._refund += refund
        self._categories[row["category"]] += gross - refund

    def snapshot(self):
        retained = self._gross - self._refund
        categories = [
            {"category": name, "retained_toman": amount,
             "share": amount / retained if retained else None}
            for name, amount in self._categories.items()
        ]
        categories.sort(key=lambda row: (-row["retained_toman"], row["category"]))
        return {"orders": self._orders, "gross_toman": self._gross,
                "refund_toman": self._refund, "retained_toman": retained,
                "categories": categories}


def check_report(report):
    """Check internal totals of a generated report, not external truth.

    This is not a general parser for arbitrary report objects.
    Shares use a dimensionless tolerance of 1e-12.
    """
    if report["gross_toman"] - report["refund_toman"] != report["retained_toman"]:
        raise ReportInvariantError("total_balance_mismatch")
    category_total = sum(row["retained_toman"] for row in report["categories"])
    if category_total != report["retained_toman"]:
        raise ReportInvariantError("category_balance_mismatch")
    for key in ("orders", "gross_toman", "refund_toman", "retained_toman"):
        if type(report[key]) is not int or report[key] < 0:
            raise ReportInvariantError("invalid_nonnegative_integer_total")
    if any(type(row["retained_toman"]) is not int or row["retained_toman"] < 0
           for row in report["categories"]):
        raise ReportInvariantError("invalid_category_amount")
    if report["retained_toman"] == 0:
        if any(row["share"] is not None for row in report["categories"]):
            raise ReportInvariantError("undefined_share_required")
    else:
        for row in report["categories"]:
            share = row["share"]
            expected = row["retained_toman"] / report["retained_toman"]
            if (not isinstance(share, (int, float)) or isinstance(share, bool)
                    or not isfinite(share) or not 0 <= share <= 1
                    or not isclose(share, expected, rel_tol=1e-12, abs_tol=1e-12)):
                raise ReportInvariantError("invalid_category_share")
        if not isclose(sum(row["share"] for row in report["categories"]),
                       1.0, rel_tol=1e-12, abs_tol=1e-12):
            raise ReportInvariantError("share_balance_mismatch")


def summarize_orders(rows):
    accumulator = ReportAccumulator()
    for record_number, row in enumerate(rows, start=1):
        accumulator.add(row, record_number)
    report = accumulator.snapshot()
    check_report(report)
    return report


def format_report(report):
    """Format a generated, already checked report; retained is not profit."""
    lines = [f"{key} {report[key]}" for key in
             ("orders", "gross_toman", "refund_toman", "retained_toman")]
    for row in report["categories"]:
        share = "NA" if row["share"] is None else f"{row['share']:.2%}"
        lines.append(f"{row['category']} {row['retained_toman']} {share}")
    return "\n".join(lines)
