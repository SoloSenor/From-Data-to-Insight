# A01
def amount_band(amount_toman):
    if amount_toman >= 1_000_000:
        return "large"
    if amount_toman >= 500_000:
        return "medium"
    return "small"

for value in [499_999, 500_000, 1_000_000]:
    print(amount_band(value))

# A03
values = [5, None, 0, 7, None]
total = 0
missing_count = 0
for value in values:
    if value is None:
        missing_count += 1
        continue
    total += value
print(total)
print(missing_count)

# A04
values = [3, 2, 1]
total = 0
for value in values:
    total += value
print(total)

# A06
def kept_amount(quantity, unit_price_toman, returned_quantity):
    return (quantity - returned_quantity) * unit_price_toman

print(kept_amount(3, 240_000, 1))
print(kept_amount(2, 80_000, 2))
print(kept_amount(2, 0, 1))

# A07
def returned_ids(orders):
    result = []
    for order in orders:
        if order["returned_quantity"] > 0:
            result.append(order["order_id"])
    return result

orders = [
    {"order_id": "O-A", "returned_quantity": 0},
    {"order_id": "O-B", "returned_quantity": 2},
]
print(returned_ids(orders))
print(returned_ids([]))

# A08
def safe_share(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator

print(safe_share(2, 4))
print(safe_share(0, 0))

# A10
def discount_for(amount_toman):
    if amount_toman >= 1_000_000:
        return 100_000
    if amount_toman >= 500_000:
        return 50_000
    return 0

assert discount_for(0) == 0
assert discount_for(499_999) == 0
assert discount_for(500_000) == 50_000
assert discount_for(999_999) == 50_000
assert discount_for(1_000_000) == 100_000
print("Discount boundary checks passed.")

# A12
def count_above(values, threshold):
    count = 0
    for value in values:
        if value > threshold:
            count += 1
    return count

print(count_above([10, 12, 12, 15], 12))
print(count_above([], 12))

