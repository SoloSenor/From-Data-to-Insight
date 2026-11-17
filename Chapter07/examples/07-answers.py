"""Independent exercise answers with shared data setup."""
orders = [
    {'order_id': 'O001', 'order_date': '2026-10-01', 'category': 'Books', 'quantity': 2, 'unit_price_toman': 120000, 'returned_quantity': 0},
    {'order_id': 'O002', 'order_date': '2026-10-01', 'category': 'Digital', 'quantity': 1, 'unit_price_toman': 800000, 'returned_quantity': 0},
    {'order_id': 'O003', 'order_date': '2026-10-02', 'category': 'Stationery', 'quantity': 5, 'unit_price_toman': 30000, 'returned_quantity': 1},
    {'order_id': 'O004', 'order_date': '2026-10-02', 'category': 'Books', 'quantity': 1, 'unit_price_toman': 200000, 'returned_quantity': 1},
    {'order_id': 'O005', 'order_date': '2026-10-03', 'category': 'Digital', 'quantity': 2, 'unit_price_toman': 450000, 'returned_quantity': 1},
    {'order_id': 'O006', 'order_date': '2026-10-03', 'category': 'Stationery', 'quantity': 3, 'unit_price_toman': 50000, 'returned_quantity': 0},
    {'order_id': 'O007', 'order_date': '2026-10-04', 'category': 'Books', 'quantity': 3, 'unit_price_toman': 100000, 'returned_quantity': 0},
    {'order_id': 'O008', 'order_date': '2026-10-04', 'category': 'Digital', 'quantity': 1, 'unit_price_toman': 1200000, 'returned_quantity': 0},
    {'order_id': 'O009', 'order_date': '2026-10-05', 'category': 'Stationery', 'quantity': 4, 'unit_price_toman': 25000, 'returned_quantity': 0},
    {'order_id': 'O010', 'order_date': '2026-10-05', 'category': 'Books', 'quantity': 2, 'unit_price_toman': 150000, 'returned_quantity': 1},
    {'order_id': 'O011', 'order_date': '2026-10-06', 'category': 'Digital', 'quantity': 1, 'unit_price_toman': 600000, 'returned_quantity': 1},
    {'order_id': 'O012', 'order_date': '2026-10-06', 'category': 'Stationery', 'quantity': 2, 'unit_price_toman': 40000, 'returned_quantity': 0},
]

# Answer 5
for position, row in enumerate(orders[:3], start=1):
    print(position, row["order_id"])

# Answer 6
full_return_ids = [
    row["order_id"] for row in orders
    if row["returned_quantity"] == row["quantity"]
]
print(full_return_ids)

# Answer 7
quantity_by_id = {row["order_id"]: row["quantity"] for row in orders}
print(quantity_by_id["O005"])

# Answer 8
ranked = sorted(orders, key=lambda row: (-row["quantity"], row["order_id"]))
print([row["order_id"] for row in ranked[:4]])

# Answer 9
ordered_units = sum(row["quantity"] for row in orders)
returned_units = sum(row["returned_quantity"] for row in orders)
print(ordered_units, returned_units)

# Answer 10
grouped = {}
for row in orders:
    name = row["category"]
    if name not in grouped:
        grouped[name] = []
    grouped[name].append(row)
for name in sorted(grouped):
    print(name, len(grouped[name]))

# Answer 11
from copy import deepcopy
original = [{"order_id": "A", "tags": ["new"]}]
changed = deepcopy(original)
changed[0]["tags"].append("checked")
print(original[0]["tags"])
print(changed[0]["tags"])

# Answer 12
category_totals = {}
for row in orders:
    name = row["category"]
    kept_units = row["quantity"] - row["returned_quantity"]
    amount = kept_units * row["unit_price_toman"]
    category_totals[name] = category_totals.get(name, 0) + amount
for name in sorted(category_totals):
    print(name, category_totals[name])
print("total", sum(category_totals.values()))

