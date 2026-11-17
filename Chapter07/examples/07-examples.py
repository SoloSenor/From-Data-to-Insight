"""Run all teaching examples in their published order."""

# Example 01
values = [10, 20]
alias = values
alias.append(30)
print(values)
print(alias is values)

# Example 02
left = [10, 20]
right = [10, 20]
print(left == right)
print(left is right)
right.append(30)
print(left)

# Example 03
original = [10, 20]
shallow = original.copy()
shallow[0] = 99
print(original)
print(shallow)
print(original is shallow)

# Example 04
source = [{"order_id": "A", "tags": ["new"]}]
shallow = source.copy()
shallow[0]["tags"].append("checked")
print(source[0]["tags"])
print(shallow is source)
print(shallow[0] is source[0])

# Example 05
source = [{"order_id": "A", "tags": ["new"]}]
copied_rows = [row.copy() for row in source]
copied_rows[0]["order_id"] = "B"
copied_rows[0]["tags"].append("checked")
print(source[0]["order_id"])
print(source[0]["tags"])
print(copied_rows[0] is source[0])

# Example 06
from copy import deepcopy
source = [{"order_id": "A", "tags": ["new"]}]
independent = deepcopy(source)
independent[0]["tags"].append("checked")
print(source[0]["tags"])
print(independent[0]["tags"])

# Example 07
bad_grid = [[0, 0]] * 3
bad_grid[0][1] = 7
print(bad_grid)
good_grid = [[0, 0] for _ in range(3)]
good_grid[0][1] = 7
print(good_grid)

# Example 08
record = ("A", ["new"])
record[1].append("checked")
print(record)

# Example 09
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
print(len(orders))
print(orders[0]["order_id"], orders[0]["category"])

# Example 10
for number, row in enumerate(orders[:3], start=1):
    print(number, row["order_id"])

# Example 11
sample = {"order_id": "O001", "category": "Books"}
for field, value in sample.items():
    print(field, value)

# Example 12
codes = ["A", "B", "C"]
quantities = [2, 5, 1]
for code, quantity in zip(codes, quantities, strict=True):
    print(code, quantity)

# Example 13
pairs = zip(["A", "B", "C"], [2, 5])
print(list(pairs))
print(list(pairs))

# Example 14
values = [2, 5, 1]
scaled_loop = []
for value in values:
    scaled_loop.append(value * 10)
scaled_comp = [value * 10 for value in values]
print(scaled_loop)
print(scaled_loop == scaled_comp)

# Example 15
returned_ids = [
    row["order_id"] for row in orders
    if row["returned_quantity"] > 0
]
print(returned_ids)

# Example 16
labels = [
    "returned" if row["returned_quantity"] > 0 else "kept"
    for row in orders[:4]
]
print(labels)

# Example 17
by_id = {row["order_id"]: row for row in orders}
print(len(by_id))
print(by_id["O005"]["category"])
print(by_id["O005"] is orders[4])

# Example 18
duplicate_rows = [
    {"order_id": "A", "quantity": 1},
    {"order_id": "A", "quantity": 9},
]
unsafe_index = {row["order_id"]: row for row in duplicate_rows}
print(len(duplicate_rows), len(unsafe_index))
print(unsafe_index["A"]["quantity"])

# Example 19
def index_unique(rows):
    index = {}
    for row in rows:
        order_id = row["order_id"]
        if order_id in index:
            raise ValueError("Duplicate order_id")
        index[order_id] = row
    return index

checked_index = index_unique(orders)
print(len(checked_index))
print(index_unique([]))

# Example 20
def quantity_key(row):
    return row["quantity"]

ranked_quantity = sorted(orders, key=quantity_key, reverse=True)
print([row["order_id"] for row in ranked_quantity[:4]])
print(orders[0]["order_id"])

# Example 21
ranked_lambda = sorted(
    orders, key=lambda row: row["quantity"], reverse=True
)
print([row["order_id"] for row in ranked_lambda[:4]])
print(ranked_lambda[0] is orders[2])

# Example 22
ranked_ties = sorted(
    orders[::-1],
    key=lambda row: (-row["quantity"], row["order_id"]),
)
print([row["order_id"] for row in ranked_ties[:6]])

# Example 23
small = [3, 1, 2]
result = small.sort()
print(small)
print(result)

# Example 24
enriched = []
for row in orders:
    item = row.copy()
    gross = row["quantity"] * row["unit_price_toman"]
    refund = row["returned_quantity"] * row["unit_price_toman"]
    item["gross_toman"] = gross
    item["refund_toman"] = refund
    item["retained_toman"] = gross - refund
    enriched.append(item)
print(enriched[0]["retained_toman"])
print("retained_toman" in orders[0])

# Example 25
totals = {}
for row in enriched:
    category = row["category"]
    totals[category] = totals.get(category, 0) + row["retained_toman"]
for category, amount in sorted(totals.items()):
    print(category, amount)

# Example 26
grand_total = sum(totals.values())
shares = {
    category: amount / grand_total
    for category, amount in totals.items()
} if grand_total else {}
print(grand_total)
for category in sorted(shares):
    print(category, f"{shares[category]:.2%}")

# Example 27
groups = {}
for row in orders:
    category = row["category"]
    if category not in groups:
        groups[category] = []
    groups[category].append(row)
print([(name, len(groups[name])) for name in sorted(groups)])
print(groups["Books"] is groups["Digital"])

# Example 28
baskets = [
    {"order_id": "A", "items": [{"sku": "P1"}, {"sku": "P2"}]},
    {"order_id": "B", "items": []},
]
lines = []
for basket in baskets:
    for item in basket["items"]:
        lines.append((basket["order_id"], item["sku"]))
print(lines)

# Example 29
numbers = [0, 0, 1, 2]
kept = [value for value in numbers if value != 0]
print(kept)
print(numbers)

# Example 30
gross_total = sum(row["gross_toman"] for row in enriched)
refund_total = sum(row["refund_toman"] for row in enriched)
retained_total = sum(row["retained_toman"] for row in enriched)
ranking = sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))
print("gross_toman", gross_total)
print("refund_toman", refund_total)
print("retained_toman", retained_total)
print("balanced", gross_total - refund_total == retained_total)
for rank, (category, amount) in enumerate(ranking, start=1):
    print(rank, category, amount)

