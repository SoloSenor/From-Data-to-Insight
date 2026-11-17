"""Reference pipeline for the clean, small teaching dataset."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
COLUMNS = ["order_id", "order_date", "category", "quantity",
           "unit_price_toman", "returned_quantity"]
DTYPES = {"order_id": str, "order_date": str, "category": str,
          "quantity": "int64", "unit_price_toman": "int64",
          "returned_quantity": "int64"}
AMOUNTS = ["gross_toman", "refund_toman", "retained_toman"]


def load_orders(path):
    """Read a CSV and reject basic violations of the teaching contract."""
    frame = pd.read_csv(path, dtype=DTYPES, encoding="utf-8")
    if list(frame.columns) != COLUMNS:
        raise ValueError("Unexpected columns or column order")
    if frame.empty or frame.isna().any().any():
        raise ValueError("Expected nonempty data without missing values")
    if not frame["order_id"].is_unique:
        raise ValueError("Duplicate order identifiers")
    if not frame["category"].isin(["Books", "Digital", "Stationery"]).all():
        raise ValueError("Unknown category")
    valid = ((frame["quantity"] > 0)
             & (frame["unit_price_toman"] >= 0)
             & (frame["returned_quantity"] >= 0)
             & (frame["returned_quantity"] <= frame["quantity"]))
    if not valid.all():
        raise ValueError("Invalid quantity, price, or returned quantity")
    return frame


def add_amounts(frame):
    """Calculate amounts for a valid, small input without changing it."""
    result = frame.copy()
    result["gross_toman"] = result["quantity"] * result["unit_price_toman"]
    result["refund_toman"] = (result["returned_quantity"]
                              * result["unit_price_toman"])
    result["retained_toman"] = result["gross_toman"] - result["refund_toman"]
    return result


def summarize_categories(frame):
    """Sum amounts by category; an all-zero denominator has no share."""
    summary = frame.groupby("category", sort=True)[AMOUNTS].sum()
    summary = summary.sort_values("retained_toman", ascending=False,
                                  kind="stable")
    total = int(summary["retained_toman"].sum())
    if total > 0:
        summary["retained_share_pct"] = summary["retained_toman"] / total * 100
    else:
        summary["retained_share_pct"] = float("nan")
    return summary


def draw_category_chart(summary):
    """Return a figure and axes; do not round the analytical values."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(summary.index, summary["retained_toman"] / 1_000_000,
           color="#287D8E")
    ax.set_title("Amount after returns by category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount after returns (million toman)")
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    return fig, ax


def main():
    orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
    summary = summarize_categories(orders)
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    summary.to_csv(output / "category-summary.csv", encoding="utf-8",
                   float_format="%.6f")
    fig, ax = draw_category_chart(summary)
    fig.savefig(output / "category-retained.png", dpi=160)
    plt.close(fig)
    totals = orders[AMOUNTS].sum()
    for name in AMOUNTS:
        print(f"{name}={int(totals[name])}")
    print(f"orders={len(orders)}")
    print(f"mean_retained_toman={orders['retained_toman'].mean():.2f}")
    print(summary.to_string(float_format=lambda value: f"{value:.2f}"))
    print("Saved: outputs/category-summary.csv")
    print("Saved: outputs/category-retained.png")


if __name__ == "__main__":
    main()
