"""Run the 24 teaching examples in order from the chapter root."""

# C01
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
DATA = ROOT / "data" / "orders.csv"
print(DATA.is_file())

# C02
values = [2, 1, 5]
quantities = np.array(values, dtype="int64")
print(values * 2)
print((quantities * 2).tolist())
print(quantities.shape)
print(str(quantities.dtype))

# C03
sample = pd.Series([240000, 800000, 120000],
                   index=["O001", "O002", "O003"],
                   name="retained_toman", dtype="int64")
print(sample.to_string())
print(int(sample.loc["O002"]))

# C04
mini = pd.DataFrame({"category": ["Books", "Digital"],
                     "quantity": [2, 1]})
print(mini.to_string(index=False))
print(type(mini["quantity"]).__name__)
print(type(mini[["quantity"]]).__name__)

# C05
dtypes = {"order_id": str, "order_date": str, "category": str,
          "quantity": "int64", "unit_price_toman": "int64",
          "returned_quantity": "int64"}
orders = pd.read_csv(DATA, dtype=dtypes, encoding="utf-8")
print(len(orders))
print(orders["order_id"].tolist())

# C06
print(orders.head(3).to_string(index=False))

# C07
print(orders.shape)
print(orders.columns.tolist())

# C08
print(orders.dtypes.to_string())

# C09
print(orders.isna().sum().to_dict())
print(orders["order_id"].is_unique)
valid_returns = ((orders["returned_quantity"] >= 0)
                 & (orders["returned_quantity"] <= orders["quantity"]))
print(bool(valid_returns.all()))

# C10
print(orders[["order_id", "category"]].head(4).to_string(index=False))

# C11
books = orders.loc[orders["category"] == "Books",
                   ["order_id", "quantity", "unit_price_toman"]]
print(books.to_string(index=False))

# C12
mask = ((orders["category"] == "Digital")
        & (orders["returned_quantity"] > 0))
digital_returns = orders.loc[mask, ["order_id", "returned_quantity"]].copy()
print(digital_returns.to_string(index=False))

# C13
orders["gross_toman"] = orders["quantity"] * orders["unit_price_toman"]
orders["refund_toman"] = (orders["returned_quantity"]
                           * orders["unit_price_toman"])
orders["retained_toman"] = orders["gross_toman"] - orders["refund_toman"]
print(orders.shape)

# C14
amount_columns = ["gross_toman", "refund_toman", "retained_toman"]
print(orders[["order_id"] + amount_columns].head(4).to_string(index=False))

# C15
totals = orders[amount_columns].sum()
for column in amount_columns:
    print(f"{column}={int(totals[column])}")

# C16
order_count = len(orders)
mean_retained = orders["retained_toman"].mean()
print(f"orders={order_count}")
print(f"mean_retained_toman={mean_retained:.2f}")

# C17
summary = orders.groupby("category", sort=True)[amount_columns].sum()
print(summary.to_string())

# C18
summary = summary.sort_values("retained_toman", ascending=False,
                               kind="stable")
print(summary["retained_toman"].to_string())

# C19
total_retained = int(orders["retained_toman"].sum())
summary["retained_share_pct"] = (summary["retained_toman"]
                                  / total_retained * 100)
print(summary[["retained_toman", "retained_share_pct"]].to_string(
    float_format=lambda value: f"{value:.2f}"))

# C20
category_counts = orders.groupby("category").size()
category_units = orders.groupby("category")["quantity"].sum()
print("order_counts:")
print(category_counts.to_string())
print("initial_units:")
print(category_units.to_string())
print(f"Digital_order_share_pct={category_counts.loc['Digital'] / len(orders) * 100:.2f}")

# C21
orders_with_return = int((orders["returned_quantity"] > 0).sum())
returned_units = int(orders["returned_quantity"].sum())
initial_units = int(orders["quantity"].sum())
refund_total = int(orders["refund_toman"].sum())
gross_total = int(orders["gross_toman"].sum())
print(f"orders_with_return={orders_with_return}")
print(f"returned_units={returned_units}")
print(f"initial_units={initial_units}")
print(f"order_return_share_pct={orders_with_return / len(orders) * 100:.2f}")
print(f"unit_return_share_pct={returned_units / initial_units * 100:.2f}")
print(f"refund_share_pct={refund_total / gross_total * 100:.2f}")

# C22
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(summary.index, summary["retained_toman"] / 1_000_000,
       color="#287D8E")
ax.set_title("Amount after returns by category")
ax.set_xlabel("Category")
ax.set_ylabel("Amount after returns (million toman)")
ax.set_ylim(bottom=0)
fig.tight_layout()
fig.savefig(OUTPUT / "category-retained.png", dpi=160)
plt.close(fig)
print("Saved: outputs/category-retained.png")

# C23
summary.to_csv(OUTPUT / "category-summary.csv", encoding="utf-8",
               float_format="%.6f")
print("Saved: outputs/category-summary.csv")
print(summary.index.name)

# C24
assert len(orders) == 12
assert orders["order_id"].is_unique
assert bool((orders["gross_toman"] ==
             orders["refund_toman"] + orders["retained_toman"]).all())
assert int(orders["gross_toman"].sum()) == 5_020_000
assert int(orders["refund_toman"].sum()) == 1_430_000
assert int(orders["retained_toman"].sum()) == 3_590_000
assert int(summary["retained_toman"].sum()) == total_retained
assert abs(float(summary["retained_share_pct"].sum()) - 100) < 1e-9
assert int(summary.loc["Books", "retained_toman"]) == 690_000
print("Checks passed")
