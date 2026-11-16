# -*- coding: utf-8 -*-
# Original, synthetic teaching examples for Chapter 03.
# Inputs: synthetic teaching example; currency unit is toman.
order_id = "O-0301"
ordered_quantity = 3
returned_quantity = 1
unit_price_toman = 240_000

# Calculations: full refund at the original unit price.
initial_amount_toman = ordered_quantity * unit_price_toman
refund_amount_toman = returned_quantity * unit_price_toman
remaining_quantity = ordered_quantity - returned_quantity
amount_after_returns_toman = initial_amount_toman - refund_amount_toman
refund_amount_ratio = refund_amount_toman / initial_amount_toman

# Display: formatting does not change the numeric values.
print(f"سفارش: {order_id}")
print(f"مبلغ اولیه: {initial_amount_toman:,} تومان")
print(f"مبلغ برگشتی: {refund_amount_toman:,} تومان")
print(f"تعداد باقی‌مانده: {remaining_quantity}")
print(f"مبلغ پس از کسر مرجوعی: {amount_after_returns_toman:,} تومان")
print(f"سهم مبلغ برگشتی از مبلغ اولیه: {refund_amount_ratio:.2%}")
