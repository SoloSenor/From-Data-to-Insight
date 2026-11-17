"""Compute amounts for trusted, already prepared order records."""


def order_amounts(quantity: int, unit_price_toman: int,
                  returned_quantity: int = 0) -> tuple[int, int, int]:
    """Return gross, refund, and retained amounts in toman.

    Preconditions: positive integer quantity, nonnegative integer price,
    and integer returned_quantity between zero and quantity. Booleans
    are not valid quantities. Inputs are not validated here.
    """
    gross = quantity * unit_price_toman
    refund = returned_quantity * unit_price_toman
    return gross, refund, gross - refund


def enrich_orders(rows: list[dict]) -> list[dict]:
    """Copy each record shallowly and add three amount fields."""
    enriched = []
    for source in rows:
        row = source.copy()
        gross, refund, retained = order_amounts(
            row["quantity"], row["unit_price_toman"],
            row["returned_quantity"],
        )
        row["gross_toman"] = gross
        row["refund_toman"] = refund
        row["retained_toman"] = retained
        enriched.append(row)
    return enriched


def group_totals(rows: list[dict]) -> dict[str, int]:
    """Sum retained amounts of enriched records by category."""
    totals = {}
    for row in rows:
        category = row["category"]
        totals[category] = totals.get(category, 0) + row["retained_toman"]
    return totals
