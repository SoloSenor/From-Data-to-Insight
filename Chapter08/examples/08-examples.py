"""Run all 30 examples in order in a fresh process."""

# Example 01
def amount(quantity, unit_price_toman):
    return quantity * unit_price_toman

result = amount(2, 120000)
print(result)

# Example 02
def show_amount(quantity, unit_price_toman):
    print(quantity * unit_price_toman)

result = show_amount(2, 120000)
print(result)

# Example 03
def amounts(quantity, unit_price_toman, returned_quantity=0):
    gross = quantity * unit_price_toman
    refund = returned_quantity * unit_price_toman
    return gross, refund, gross - refund

gross, refund, retained = amounts(2, 450000, 1)
print(gross, refund, retained)

# Example 04
print(amounts(returned_quantity=1, unit_price_toman=450000,
              quantity=2))
print(amounts(2, unit_price_toman=450000, returned_quantity=1))

# Example 05
print(amounts(2, 450000))
print(amounts(2, 450000, returned_quantity=2))

# Example 06
def meets_minimum(value, *, minimum=0):
    return value >= minimum

print(meets_minimum(450000, minimum=500000))
print(meets_minimum(690000, minimum=500000))

# Example 07
values = (2, 450000, 1)
print(amounts(*values))

# Example 08
options = {"quantity": 2, "unit_price_toman": 450000,
           "returned_quantity": 1}
print(amounts(**options))

# Example 09
def total_amount(*values):
    return sum(values)

print(total_amount(240000, 450000, 300000))
print(total_amount())

# Example 10
def field_names(**fields):
    return sorted(fields)

print(field_names(order_id="A", category="Books"))

# Example 11
label = "global"
def local_label():
    label = "local"
    return label

print(local_label())
print(label)

# Example 12
def outer():
    label = "enclosing"
    def inner():
        return label
    return inner()

print(outer())

# Example 13
unit_price = 120000
def hidden_amount(quantity):
    return quantity * unit_price

print(hidden_amount(2))
unit_price = 150000
print(hidden_amount(2))
print(amount(2, 120000))

# Example 14
def replace_quantity(quantity):
    quantity = 99
    return quantity

quantity = 2
print(replace_quantity(quantity))
print(quantity)

# Example 15
def add_in_place(values, value):
    values.append(value)

def added(values, value):
    return values + [value]

source = [10]
print(add_in_place(source, 20))
print(source)
print(added(source, 30))
print(source)

# Example 16
def remember_bad(value, items=[]):
    items.append(value)
    return items

print(remember_bad("A"))
print(remember_bad("B"))

# Example 17
def remembered(value, items=None):
    result = [] if items is None else items.copy()
    result.append(value)
    return result

print(remembered("A"))
print(remembered("B"))
source = ["old"]
print(remembered("new", source))
print(source)

# Example 18
limit = 10
def configured_limit(value=limit):
    return value

limit = 20
print(configured_limit())
print(configured_limit(limit))

# Example 19
def net_units(quantity, returned_quantity=0):
    """Return retained units for a valid single-item order."""
    return quantity - returned_quantity

print(net_units.__doc__)
print(net_units(5, 1))

# Example 20
def identity_number(value: int) -> int:
    return value

print(identity_number(10))
print(identity_number("not checked"))

# Example 21
def apply_amount(quantity, price, calculator):
    return calculator(quantity, price)

print(apply_amount(2, 120000, amount))

# Example 22
import math
from statistics import mean as average

print(math.isclose(0.1 + 0.2, 0.3))
print(average([10, 20, 30]))

# Example 23
value = complex(3, 4)
print(value.real)
print(value.imag)
print(value.conjugate())

# Example 24
values = [30, 10, 20]
result = values.sort()
print(values)
print(result)

# Example 25
calculator = amount
print(callable(calculator))
print(calculator.__name__)
print(calculator(2, 120000))

# Example 26
from inspect import signature

def priced(quantity: int, unit_price_toman: int = 100) -> int:
    return quantity * unit_price_toman

print(signature(priced))

# Example 27
import statistics as stats

print(stats.__name__)
print(stats.mean.__name__)
print(callable(stats.mean))

# Example 28
first = amounts(2, 450000, 1)
second = amounts(2, 450000, 1)
print(first == second)
print(first)

# Example 29
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
print(sum(amounts(row["quantity"], row["unit_price_toman"],
                  row["returned_quantity"])[2] for row in orders))

# Example 30
def select_category(rows, category):
    return [row.copy() for row in rows if row["category"] == category]

books = select_category(orders, "Books")
books[0]["quantity"] = 99
print(len(books))
print(orders[0]["quantity"])
