"""Small trusted-record analysis; standard library only."""

def index_unique(rows):
    index = {}
    for row in rows:
        order_id = row["order_id"]
        if order_id in index:
            raise ValueError("Duplicate order_id")
        index[order_id] = row
    return index


def build_report(rows):
    """Do not mutate input; numeric fields must already be valid integers."""
    index_unique(rows)
    enriched = []
    totals = {}
    gross_total = 0
    refund_total = 0
    for row in rows:
        item = row.copy()
        gross = row["quantity"] * row["unit_price_toman"]
        refund = row["returned_quantity"] * row["unit_price_toman"]
        retained = gross - refund
        item["gross_toman"] = gross
        item["refund_toman"] = refund
        item["retained_toman"] = retained
        enriched.append(item)
        category = row["category"]
        totals[category] = totals.get(category, 0) + retained
        gross_total += gross
        refund_total += refund
    retained_total = gross_total - refund_total
    ranked = sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))
    groups = []
    for category, amount in ranked:
        groups.append({
            "category": category,
            "retained_toman": amount,
            "share": amount / retained_total if retained_total else None,
        })
    return {
        "order_count": len(rows),
        "gross_toman": gross_total,
        "refund_toman": refund_total,
        "retained_toman": retained_total,
        "groups": groups,
        "rows": enriched,
    }
