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
