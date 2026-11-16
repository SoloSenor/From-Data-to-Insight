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
