# Python 3; ASCII-only code and output.

# BEGIN A01
values = [5, 2, 8, 1]
print(values[-1])
print(values[1:3])
print(values[10:])
# END A01

# BEGIN A02
first = [1, 2]
second = [1, 2]
first.append([3, 4])
second.extend([3, 4])
print(first, len(first))
print(second, len(second))
# END A02

# BEGIN A03
statuses = ["paid", "new", "paid"]
statuses.remove("paid")
removed_status = statuses.pop()
print(statuses)
print(removed_status)
# END A03

# BEGIN A04
amounts_toman = [90_000, 10_000, 50_000]
print(sorted(amounts_toman, reverse=True))
print(amounts_toman)
# END A04

# BEGIN A06
order = {"order_id": "O-0411", "quantity": 4, "unit_price_toman": 75_000}
print(order["order_id"])
print(order["quantity"] * order["unit_price_toman"])
# END A06

# BEGIN A08
single_id = ("O-0412",)
print(len(single_id))
lower, upper = (0, 10)
print(upper - lower)
# END A08

# BEGIN A09
expected = {"O-0401", "O-0402", "O-0403"}
received = {"O-0402", "O-0404"}
print(sorted(expected - received))
print(sorted(received - expected))
# END A09

# BEGIN A12
order = {"quantity": 2, "unit_price_toman": 50_000, "returned_quantity": 2}
gross_toman = order["quantity"] * order["unit_price_toman"]
refund_toman = order["returned_quantity"] * order["unit_price_toman"]
print(gross_toman)
print(refund_toman)
print(gross_toman - refund_toman)
# END A12
