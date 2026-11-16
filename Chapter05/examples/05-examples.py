# C01
quantity = 3
returned_quantity = 1
print(quantity == 3)
print(quantity != 3)
print(0 <= returned_quantity <= quantity)
print((quantity > 0) and (returned_quantity > 0))
print((returned_quantity == 0) or (returned_quantity == quantity))
print(not (returned_quantity > 0))

# C02
print(bool(0))
print(bool(None))
print(bool([]))
print(bool([0]))
print(bool("0"))
print(bool("False"))

# C03
returned_quantity = 0
if returned_quantity > 0:
    print("has_return")
else:
    print("no_return")
print("checked")

# C04
quantity = 3
returned_quantity = 1
if returned_quantity == 0:
    status = "no_return"
elif returned_quantity == quantity:
    status = "full_return"
else:
    status = "partial_return"
print(status)

# C05
amount_toman = 1_200_000
if amount_toman >= 500_000:
    print("medium_or_more")
if amount_toman >= 1_000_000:
    print("large")

if amount_toman >= 1_000_000:
    print("tier_large")
elif amount_toman >= 500_000:
    print("tier_medium")
else:
    print("tier_small")

# C06
quantity = 0
returned_quantity = 0
has_high_return = (quantity > 0) and (returned_quantity / quantity > 0.5)
print(has_high_return)

# C07
returned_quantity = None
if returned_quantity is None:
    print("unknown")
elif returned_quantity == 0:
    print("no_return")
else:
    print("has_return")

print(0 or 99)

# C08
orders = [
    {"order_id": "O-0401", "quantity": 3},
    {"order_id": "O-0402", "quantity": 2},
    {"order_id": "O-0403", "quantity": 1},
]
for order in orders:
    print(order["order_id"], order["quantity"])
print("done")

# C09
for number in range(1, 4):
    print(number)
print(list(range(3)))
print(list(range(3, 0, -1)))

# C10
orders = [
    {"quantity": 3, "returned_quantity": 1},
    {"quantity": 2, "returned_quantity": 0},
    {"quantity": 1, "returned_quantity": 1},
]
total_quantity = 0
orders_with_return = 0
for order in orders:
    total_quantity += order["quantity"]
    if order["returned_quantity"] > 0:
        orders_with_return += 1
print(total_quantity)
print(orders_with_return)

# C11
orders = [
    {"order_id": "O-0401", "returned_quantity": 1},
    {"order_id": "O-0402", "returned_quantity": 0},
    {"order_id": "O-0403", "returned_quantity": 1},
]
selected_ids = []
for order in orders:
    if order["returned_quantity"] > 0:
        selected_ids.append(order["order_id"])
print(selected_ids)
print(len(orders))

# C12
values = [10, None, 0, 20]
total = 0
missing_count = 0
for value in values:
    if value is None:
        missing_count += 1
        continue
    total += value
print(total)
print(missing_count)

# C13
values = [0, 0, 2, 5]
first_positive = None
for value in values:
    if value > 0:
        first_positive = value
        break
print(first_positive)

# C14
attempt = 1
while attempt <= 3:
    print("attempt", attempt)
    attempt += 1
print("finished")

# C15
def line_amount(quantity, unit_price_toman):
    return quantity * unit_price_toman

print("defined")
amount_toman = line_amount(3, 240_000)
print(amount_toman)
print(line_amount(quantity=2, unit_price_toman=80_000))

# C16
def show_amount(quantity, unit_price_toman):
    print(quantity * unit_price_toman)

def calculate_amount(quantity, unit_price_toman):
    return quantity * unit_price_toman

shown_result = show_amount(2, 80_000)
calculated_result = calculate_amount(2, 80_000)
print(shown_result)
print(calculated_result + 40_000)

# C17
quantity = 99

def double_quantity(quantity):
    doubled = quantity * 2
    return doubled

print(double_quantity(3))
print(quantity)

# C18
def return_status(quantity, returned_quantity):
    if returned_quantity == 0:
        return "no_return"
    if returned_quantity == quantity:
        return "full_return"
    return "partial_return"

def return_amounts(quantity, unit_price_toman, returned_quantity):
    gross_toman = quantity * unit_price_toman
    refund_toman = returned_quantity * unit_price_toman
    return {
        "gross_toman": gross_toman,
        "refund_toman": refund_toman,
        "after_returns_toman": gross_toman - refund_toman,
    }

result = return_amounts(3, 240_000, 1)
print(result["after_returns_toman"])
print(return_status(3, 1))

# C19
def discount_for(amount_toman):
    if amount_toman >= 1_000_000:
        return 100_000
    if amount_toman >= 500_000:
        return 50_000
    return 0

def quote_order(quantity, unit_price_toman):
    gross_toman = quantity * unit_price_toman
    discount_toman = discount_for(gross_toman)
    return {
        "gross_toman": gross_toman,
        "discount_toman": discount_toman,
        "payable_toman": gross_toman - discount_toman,
    }

quote = quote_order(3, 240_000)
print(quote["gross_toman"])
print(quote["discount_toman"])
print(quote["payable_toman"])

# C20
def discount_for(amount_toman):
    if amount_toman >= 1_000_000:
        return 100_000
    if amount_toman >= 500_000:
        return 50_000
    return 0

for amount_toman in [499_999, 500_000, 999_999, 1_000_000]:
    print(amount_toman, discount_for(amount_toman))

# C21
def return_status(quantity, returned_quantity):
    if returned_quantity == 0:
        return "no_return"
    if returned_quantity == quantity:
        return "full_return"
    return "partial_return"


def analyze_order(order):
    quantity = order["quantity"]
    unit_price_toman = order["unit_price_toman"]
    returned_quantity = order["returned_quantity"]
    gross_toman = quantity * unit_price_toman
    refund_toman = returned_quantity * unit_price_toman
    return {
        "order_id": order["order_id"],
        "quantity": quantity,
        "returned_quantity": returned_quantity,
        "gross_toman": gross_toman,
        "refund_toman": refund_toman,
        "after_returns_toman": gross_toman - refund_toman,
        "return_status": return_status(quantity, returned_quantity),
    }


def summarize_orders(orders):
    report = {
        "order_count": 0,
        "total_quantity": 0,
        "total_returned_quantity": 0,
        "orders_with_return": 0,
        "gross_toman": 0,
        "refund_toman": 0,
        "after_returns_toman": 0,
    }
    for order in orders:
        result = analyze_order(order)
        report["order_count"] += 1
        report["total_quantity"] += result["quantity"]
        report["total_returned_quantity"] += result["returned_quantity"]
        report["gross_toman"] += result["gross_toman"]
        report["refund_toman"] += result["refund_toman"]
        report["after_returns_toman"] += result["after_returns_toman"]
        if result["returned_quantity"] > 0:
            report["orders_with_return"] += 1
    return report

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

for order in orders:
    result = analyze_order(order)
    print(result["order_id"], result["return_status"], result["after_returns_toman"])
report = summarize_orders(orders)
for key in report:
    print(key, report[key])

# C22
def return_status(quantity, returned_quantity):
    if returned_quantity == 0:
        return "no_return"
    if returned_quantity == quantity:
        return "full_return"
    return "partial_return"


def analyze_order(order):
    quantity = order["quantity"]
    unit_price_toman = order["unit_price_toman"]
    returned_quantity = order["returned_quantity"]
    gross_toman = quantity * unit_price_toman
    refund_toman = returned_quantity * unit_price_toman
    return {
        "order_id": order["order_id"],
        "quantity": quantity,
        "returned_quantity": returned_quantity,
        "gross_toman": gross_toman,
        "refund_toman": refund_toman,
        "after_returns_toman": gross_toman - refund_toman,
        "return_status": return_status(quantity, returned_quantity),
    }


def summarize_orders(orders):
    report = {
        "order_count": 0,
        "total_quantity": 0,
        "total_returned_quantity": 0,
        "orders_with_return": 0,
        "gross_toman": 0,
        "refund_toman": 0,
        "after_returns_toman": 0,
    }
    for order in orders:
        result = analyze_order(order)
        report["order_count"] += 1
        report["total_quantity"] += result["quantity"]
        report["total_returned_quantity"] += result["returned_quantity"]
        report["gross_toman"] += result["gross_toman"]
        report["refund_toman"] += result["refund_toman"]
        report["after_returns_toman"] += result["after_returns_toman"]
        if result["returned_quantity"] > 0:
            report["orders_with_return"] += 1
    return report

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

orders.append({
    "order_id": "O-0404",
    "quantity": 2,
    "unit_price_toman": 50_000,
    "returned_quantity": 0,
})
report = summarize_orders(orders)
print(report["order_count"])
print(report["total_quantity"])
print(report["gross_toman"])
print(report["refund_toman"])
print(report["after_returns_toman"])

# C23
def return_status(quantity, returned_quantity):
    if returned_quantity == 0:
        return "no_return"
    if returned_quantity == quantity:
        return "full_return"
    return "partial_return"


def analyze_order(order):
    quantity = order["quantity"]
    unit_price_toman = order["unit_price_toman"]
    returned_quantity = order["returned_quantity"]
    gross_toman = quantity * unit_price_toman
    refund_toman = returned_quantity * unit_price_toman
    return {
        "order_id": order["order_id"],
        "quantity": quantity,
        "returned_quantity": returned_quantity,
        "gross_toman": gross_toman,
        "refund_toman": refund_toman,
        "after_returns_toman": gross_toman - refund_toman,
        "return_status": return_status(quantity, returned_quantity),
    }


def summarize_orders(orders):
    report = {
        "order_count": 0,
        "total_quantity": 0,
        "total_returned_quantity": 0,
        "orders_with_return": 0,
        "gross_toman": 0,
        "refund_toman": 0,
        "after_returns_toman": 0,
    }
    for order in orders:
        result = analyze_order(order)
        report["order_count"] += 1
        report["total_quantity"] += result["quantity"]
        report["total_returned_quantity"] += result["returned_quantity"]
        report["gross_toman"] += result["gross_toman"]
        report["refund_toman"] += result["refund_toman"]
        report["after_returns_toman"] += result["after_returns_toman"]
        if result["returned_quantity"] > 0:
            report["orders_with_return"] += 1
    return report

report = summarize_orders([])
print(report["order_count"])
print(report["gross_toman"])
print(report["after_returns_toman"])
if report["order_count"] == 0:
    order_return_share = None
else:
    order_return_share = report["orders_with_return"] / report["order_count"]
print(order_return_share)

# C24
def return_status(quantity, returned_quantity):
    if returned_quantity == 0:
        return "no_return"
    if returned_quantity == quantity:
        return "full_return"
    return "partial_return"


def analyze_order(order):
    quantity = order["quantity"]
    unit_price_toman = order["unit_price_toman"]
    returned_quantity = order["returned_quantity"]
    gross_toman = quantity * unit_price_toman
    refund_toman = returned_quantity * unit_price_toman
    return {
        "order_id": order["order_id"],
        "quantity": quantity,
        "returned_quantity": returned_quantity,
        "gross_toman": gross_toman,
        "refund_toman": refund_toman,
        "after_returns_toman": gross_toman - refund_toman,
        "return_status": return_status(quantity, returned_quantity),
    }


def summarize_orders(orders):
    report = {
        "order_count": 0,
        "total_quantity": 0,
        "total_returned_quantity": 0,
        "orders_with_return": 0,
        "gross_toman": 0,
        "refund_toman": 0,
        "after_returns_toman": 0,
    }
    for order in orders:
        result = analyze_order(order)
        report["order_count"] += 1
        report["total_quantity"] += result["quantity"]
        report["total_returned_quantity"] += result["returned_quantity"]
        report["gross_toman"] += result["gross_toman"]
        report["refund_toman"] += result["refund_toman"]
        report["after_returns_toman"] += result["after_returns_toman"]
        if result["returned_quantity"] > 0:
            report["orders_with_return"] += 1
    return report

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

report = summarize_orders(orders)
order_share = report["orders_with_return"] / report["order_count"]
unit_share = report["total_returned_quantity"] / report["total_quantity"]
amount_share = report["refund_toman"] / report["gross_toman"]
print(f"order_return_share: {order_share:.2%}")
print(f"unit_return_share: {unit_share:.2%}")
print(f"refund_amount_share: {amount_share:.2%}")

# C25
def discount_for(amount_toman):
    if amount_toman >= 1_000_000:
        return 100_000
    if amount_toman >= 500_000:
        return 50_000
    return 0

def quote_order(quantity, unit_price_toman):
    gross_toman = quantity * unit_price_toman
    discount_toman = discount_for(gross_toman)
    return {
        "gross_toman": gross_toman,
        "discount_toman": discount_toman,
        "payable_toman": gross_toman - discount_toman,
    }

def return_status(quantity, returned_quantity):
    if returned_quantity == 0:
        return "no_return"
    if returned_quantity == quantity:
        return "full_return"
    return "partial_return"


def analyze_order(order):
    quantity = order["quantity"]
    unit_price_toman = order["unit_price_toman"]
    returned_quantity = order["returned_quantity"]
    gross_toman = quantity * unit_price_toman
    refund_toman = returned_quantity * unit_price_toman
    return {
        "order_id": order["order_id"],
        "quantity": quantity,
        "returned_quantity": returned_quantity,
        "gross_toman": gross_toman,
        "refund_toman": refund_toman,
        "after_returns_toman": gross_toman - refund_toman,
        "return_status": return_status(quantity, returned_quantity),
    }


def summarize_orders(orders):
    report = {
        "order_count": 0,
        "total_quantity": 0,
        "total_returned_quantity": 0,
        "orders_with_return": 0,
        "gross_toman": 0,
        "refund_toman": 0,
        "after_returns_toman": 0,
    }
    for order in orders:
        result = analyze_order(order)
        report["order_count"] += 1
        report["total_quantity"] += result["quantity"]
        report["total_returned_quantity"] += result["returned_quantity"]
        report["gross_toman"] += result["gross_toman"]
        report["refund_toman"] += result["refund_toman"]
        report["after_returns_toman"] += result["after_returns_toman"]
        if result["returned_quantity"] > 0:
            report["orders_with_return"] += 1
    return report

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

assert discount_for(499_999) == 0
assert discount_for(500_000) == 50_000
assert discount_for(1_000_000) == 100_000
assert quote_order(3, 240_000)["payable_toman"] == 670_000
assert return_status(3, 0) == "no_return"
assert return_status(3, 1) == "partial_return"
assert return_status(3, 3) == "full_return"
assert analyze_order(orders[0])["after_returns_toman"] == 480_000
report = summarize_orders(orders)
assert report["gross_toman"] == 1_180_000
assert report["refund_toman"] == 540_000
assert report["after_returns_toman"] == 640_000
assert summarize_orders([])["order_count"] == 0
print("All sample checks passed.")

