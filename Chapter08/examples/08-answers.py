"""Run the coding exercise answers in order."""
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

# Exercise 5
def retained_units(quantity, returned_quantity=0):
    return quantity - returned_quantity

print(retained_units(5, 1))
print(retained_units(5))

# Exercise 6
def kept_amount(quantity, price, *, returned=0):
    return (quantity - returned) * price

print(kept_amount(2, 450000, returned=1))

# Exercise 7
def share_of_total(amount, denominator):
    return None if denominator == 0 else amount / denominator

print(share_of_total(25, 100))
print(share_of_total(0, 0))

# Exercise 8
def with_note(note, notes=None):
    result = [] if notes is None else notes.copy()
    result.append(note)
    return result

source = ["old"]
print(with_note("A"))
print(with_note("B"))
print(with_note("new", source))
print(source)

# Exercise 9
def retained_value(quantity: int, price: int, returned: int = 0) -> int:
    """Return retained value in toman for valid integer inputs."""
    return (quantity - returned) * price

print(retained_value.__doc__)
print(retained_value(2, 450000, 1))

# Exercise 10
def visible_groups(groups, *, minimum=0):
    return [group.copy() for group in groups
            if group["retained_toman"] >= minimum]

groups = [{"category": "Digital", "retained_toman": 2450000},
          {"category": "Books", "retained_toman": 690000},
          {"category": "Stationery", "retained_toman": 450000}]
selected = visible_groups(groups, minimum=500000)
print([group["category"] for group in selected])
print(len(groups))

# Exercise 11
def order_total(rows):
    return sum((row["quantity"] - row["returned_quantity"])
               * row["unit_price_toman"] for row in rows)

print(order_total(orders))
print(order_total([]))

# Exercise 12
def summary_text(total: int) -> str:
    return f"retained_toman {total}"

def display_summary(total: int) -> None:
    print(summary_text(total))

text = summary_text(3590000)
print(text == "retained_toman 3590000")
display_summary(3590000)
