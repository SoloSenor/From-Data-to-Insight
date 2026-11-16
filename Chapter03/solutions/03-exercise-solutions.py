# -*- coding: utf-8 -*-
# Original, synthetic teaching examples for Chapter 03.
# A03
ordered_quantity = 4
returned_quantity = 1
unit_price_toman = 125_000
amount_after_returns_toman = (ordered_quantity - returned_quantity) * unit_price_toman
print(amount_after_returns_toman)

# A04
item_count = 29
items_per_box = 8
print(item_count // items_per_box)
print(item_count % items_per_box)

# A06
initial_amount_toman = 800_000
refund_amount_toman = 120_000
refund_amount_ratio = refund_amount_toman / initial_amount_toman
print(refund_amount_ratio)
print(f"{refund_amount_ratio:.1%}")

# A10
order_id = "O-0302"
ordered_quantity = 5
returned_quantity = 2
unit_price_toman = 180_000
initial_amount_toman = ordered_quantity * unit_price_toman
refund_amount_toman = returned_quantity * unit_price_toman
remaining_quantity = ordered_quantity - returned_quantity
amount_after_returns_toman = initial_amount_toman - refund_amount_toman
refund_amount_ratio = refund_amount_toman / initial_amount_toman
print(f"سفارش: {order_id}")
print(f"مبلغ اولیه: {initial_amount_toman:,} تومان")
print(f"مبلغ برگشتی: {refund_amount_toman:,} تومان")
print(f"تعداد باقی‌مانده: {remaining_quantity}")
print(f"مبلغ پس از کسر مرجوعی: {amount_after_returns_toman:,} تومان")
print(f"سهم مبلغ برگشتی: {refund_amount_ratio:.1%}")
