# Python 3; ASCII-only code and output.

# BEGIN C01
quantities = [3, 1, 4, 2]
print(quantities)
print(len(quantities))
print(quantities[0])
print(quantities[-1])
# END C01

# BEGIN C02
quantities = [3, 1, 4, 2]
print(quantities[1:3])
print(quantities[:2])
print(quantities[2:])
print(quantities[::2])
print(quantities[::-1])
print(quantities)
# END C02

# BEGIN C03
quantities = [3, 1, 4, 2]
print(quantities[:99])
print(quantities[99:])
print(quantities[2:2])
print([][:2])
# END C03

# BEGIN C04
quantities = [3, 1, 4]
quantities[1] = 2
print(quantities)
# END C04

# BEGIN C05
first = [3, 1]
first.append([4, 2])
second = [3, 1]
second.extend([4, 2])
print(first)
print(len(first))
print(second)
print(len(second))
# END C05

# BEGIN C06
order_ids = ["O-0401", "O-0403"]
order_ids.insert(1, "O-0402")
removed_id = order_ids.pop()
print(order_ids)
print(removed_id)
# END C06

# BEGIN C07
labels = ["new", "paid", "new", "sent"]
labels.remove("new")
print(labels)
del labels[1]
print(labels)
# END C07

# BEGIN C08
categories = ["book", "pen", "book"]
print("book" in categories)
print("bag" in categories)
print(categories.count("book"))
print(len(categories))
# END C08

# BEGIN C09
amounts_toman = [720_000, 160_000, 300_000]
ascending = sorted(amounts_toman)
print(ascending)
print(amounts_toman)
result = amounts_toman.sort(reverse=True)
print(amounts_toman)
print(result)
# END C09

# BEGIN C10
original = [3, 1, 4]
alias = original
alias[0] = 9
print(original)
print(alias)
# END C10

# BEGIN C11
original = [3, 1, 4]
working = original.copy()
working[0] = 9
print(original)
print(working)
# END C11

# BEGIN C12
order = {
    "order_id": "O-0401",
    "quantity": 3,
    "unit_price_toman": 240_000,
}
print(order["order_id"])
print(order["quantity"] * order["unit_price_toman"])
print(len(order))
# END C12

# BEGIN C13
order = {"order_id": "O-0401", "quantity": 3}
order["status"] = "new"
order["quantity"] = 2
order["temporary_note"] = "check"
del order["temporary_note"]
print(order)
# END C13

# BEGIN C14
order = {"shipping_toman": None, "discount_toman": 0}
print(order.get("shipping_toman", 50_000))
print(order.get("discount_toman", 50_000))
print(order.get("tax_toman", 50_000))
print("tax_toman" in order)
# END C14

# BEGIN C15
order = {"order_id": "O-0401", "quantity": 3}
print("order_id" in order)
print("O-0401" in order)
print(list(order.keys()))
print(list(order.values()))
print(list(order.items()))
# END C15

# BEGIN C16
amount_by_id = {"O-0401": 720_000}
amount_by_id["O-0401"] = 480_000
print(len(amount_by_id))
print(amount_by_id["O-0401"])
# END C16

# BEGIN C17
price_bounds_toman = (100_000, 300_000)
minimum_toman, maximum_toman = price_bounds_toman
single_id = ("O-0401",)
print(price_bounds_toman[0])
print(minimum_toman, maximum_toman)
print(type(single_id).__name__)
print(type(("O-0401")).__name__)
# END C17

# BEGIN C18
record = ("O-0401", [3, 1])
record[1].append(4)
print(record)
# END C18

# BEGIN C19
categories = ["book", "pen", "book", "bag"]
unique_categories = set(categories)
print(len(categories))
print(len(unique_categories))
print(sorted(unique_categories))
print("pen" in unique_categories)
# END C19

# BEGIN C20
expected_ids = {"O-0401", "O-0402", "O-0403"}
received_ids = {"O-0401", "O-0403", "O-0404"}
print(sorted(expected_ids & received_ids))
print(sorted(expected_ids - received_ids))
print(sorted(received_ids - expected_ids))
print(sorted(expected_ids | received_ids))
received_ids.add("O-0404")
print(len(received_ids))
# END C20

# BEGIN C21
orders = [
    {"order_id": "O-0401", "quantity": 3, "unit_price_toman": 240_000},
    {"order_id": "O-0402", "quantity": 2, "unit_price_toman": 80_000},
]
print(len(orders))
print(orders[0]["order_id"])
print(orders[1]["quantity"])
print(orders[1]["quantity"] * orders[1]["unit_price_toman"])
# END C21

# BEGIN C22
order_ids = ["O-0401", "O-0402", "O-0403"]
amounts_toman = [720_000, 160_000, 300_000]
amounts_toman.sort()
print(order_ids[0], amounts_toman[0])
print(len(order_ids) == len(amounts_toman))
# END C22

# BEGIN C23
order = {"quantity": 3, "unit_price_toman": 240_000}
order["gross_toman"] = order["quantity"] * order["unit_price_toman"]
order["quantity"] = 2
print(order["gross_toman"])
print(order["quantity"] * order["unit_price_toman"])
# END C23

# BEGIN C24
orders = [
    {
        "order_id": "O-0401",
        "quantity": 3,
        "unit_price_toman": 240_000,
        "returned_quantity": 1,
    },
    {
        "order_id": "O-0402",
        "quantity": 2,
        "unit_price_toman": 80_000,
        "returned_quantity": 0,
    },
    {
        "order_id": "O-0403",
        "quantity": 1,
        "unit_price_toman": 300_000,
        "returned_quantity": 1,
    },
]

first = orders[0]
second = orders[1]
third = orders[2]

gross_amounts_toman = [
    first["quantity"] * first["unit_price_toman"],
    second["quantity"] * second["unit_price_toman"],
    third["quantity"] * third["unit_price_toman"],
]
refund_amounts_toman = [
    first["returned_quantity"] * first["unit_price_toman"],
    second["returned_quantity"] * second["unit_price_toman"],
    third["returned_quantity"] * third["unit_price_toman"],
]

gross_total_toman = sum(gross_amounts_toman)
refund_total_toman = sum(refund_amounts_toman)
after_returns_toman = gross_total_toman - refund_total_toman

print(f"Order records: {len(orders)}")
print(f"Gross amounts: {gross_amounts_toman}")
print(f"Refund amounts: {refund_amounts_toman}")
print(f"Gross total (toman): {gross_total_toman:,}")
print(f"Refund total (toman): {refund_total_toman:,}")
print(f"After returns (toman): {after_returns_toman:,}")
# END C24
