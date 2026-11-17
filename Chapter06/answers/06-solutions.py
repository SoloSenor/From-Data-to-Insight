"""Eight exercise solutions; run this file from any working directory."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# A01
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
mask = orders["returned_quantity"] == orders["quantity"]
print(orders.loc[mask, "order_id"].tolist())
print(int(mask.sum()))


# A02
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
mask = ((orders["returned_quantity"] > 0)
        & (orders["returned_quantity"] < orders["quantity"]))
print(orders.loc[mask, "order_id"].tolist())


# A03
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
mask = orders["retained_toman"] >= 300000
print(orders.loc[mask, ["order_id", "retained_toman"]].to_string(index=False))


# A04
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
orders["retained_units"] = orders["quantity"] - orders["returned_quantity"]
units = orders.groupby("category")["retained_units"].sum()
print(units.to_string())
print(f"total_retained_units={int(units.sum())}")


# A05
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
summary = summarize_categories(orders)
summary["refund_share_pct"] = summary["refund_toman"] / summary["gross_toman"] * 100
print(summary["refund_share_pct"].sort_index().to_string(float_format=lambda x: f"{x:.2f}"))


# A06
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
means = orders.groupby("category")["retained_toman"].mean()
print(means.to_string(float_format=lambda x: f"{x:.2f}"))


# A07
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
extra = pd.DataFrame([{"order_id": "O013", "order_date": "2026-10-07",
                       "category": "Books", "quantity": 1,
                       "unit_price_toman": 100000, "returned_quantity": 0}])
columns = ["order_id", "order_date", "category", "quantity",
           "unit_price_toman", "returned_quantity"]
expanded = add_amounts(pd.concat([orders[columns], extra], ignore_index=True))
summary = summarize_categories(expanded)
print(f"total_retained_toman={int(expanded['retained_toman'].sum())}")
print(f"Books_share_pct={summary.loc['Books', 'retained_share_pct']:.2f}")


# A08
from analysis import load_orders, add_amounts, summarize_categories, ROOT
import pandas as pd
orders = add_amounts(load_orders(ROOT / "data/orders.csv"))
full_returns = orders.copy()
full_returns["returned_quantity"] = full_returns["quantity"]
summary = summarize_categories(add_amounts(full_returns))
print(summary["retained_toman"].to_dict())
print(bool(summary["retained_share_pct"].isna().all()))
