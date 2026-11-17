"""Build a complete report before choosing its text presentation."""
from .metrics import enrich_orders, group_totals


def check_unique_ids(rows: list[dict]) -> None:
    """Reject duplicate IDs; do not perform full schema validation."""
    seen = set()
    for row in rows:
        key = row["order_id"]
        if key in seen:
            raise ValueError("Duplicate order_id")
        seen.add(key)


def rank_groups(totals: dict[str, int], denominator: int) -> list[dict]:
    """Rank by descending amount, then ascending category name."""
    groups = []
    for category, amount in totals.items():
        share = amount / denominator if denominator else None
        groups.append({"category": category, "retained_toman": amount,
                       "share": share})
    return sorted(groups, key=lambda group: (
        -group["retained_toman"], group["category"],
    ))


def build_report(rows: list[dict]) -> dict:
    """Build a report without changing record fields or input order.

    Accept a reusable list of valid, single-item orders. Only duplicate
    IDs are explicitly rejected. Copies of row dictionaries are shallow.
    """
    check_unique_ids(rows)
    enriched = enrich_orders(rows)
    gross = sum(row["gross_toman"] for row in enriched)
    refund = sum(row["refund_toman"] for row in enriched)
    retained = gross - refund
    return {
        "order_count": len(rows),
        "gross_toman": gross,
        "refund_toman": refund,
        "retained_toman": retained,
        "groups": rank_groups(group_totals(enriched), retained),
        "rows": enriched,
    }


def format_report(report: dict, *, minimum_toman: int = 0) -> str:
    """Format text; filter displayed groups without recalculating shares.

    minimum_toman must be a nonnegative integer. It is not validated here.
    Group shares keep the complete report denominator, even when some
    group lines are hidden. No trailing newline is added.
    """
    lines = [
        f"orders {report['order_count']}",
        f"gross_toman {report['gross_toman']}",
        f"refund_toman {report['refund_toman']}",
        f"retained_toman {report['retained_toman']}",
    ]
    for group in report["groups"]:
        amount = group["retained_toman"]
        if amount >= minimum_toman:
            share = group["share"]
            share_text = "NA" if share is None else f"{share:.2%}"
            lines.append(f"{group['category']} {amount} {share_text}")
    return "\n".join(lines)
