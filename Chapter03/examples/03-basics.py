# -*- coding: utf-8 -*-
# Original, synthetic teaching examples for Chapter 03.
# C01
print(type(3))
print(type(240_000))
print(type(0.1))
print(type("O-0301"))
print(type(True))
print(type(None))

# C02
quantity = 3
unit_price_toman = 240_000
initial_amount_toman = quantity * unit_price_toman
print(initial_amount_toman)

# C03
quantity = 3
saved_quantity = quantity
quantity = 5
print(quantity)
print(saved_quantity)

# C04
quantity = 3
unit_price_toman = 240_000
amount_toman = quantity * unit_price_toman
quantity = 4
print(amount_toman)
amount_toman = quantity * unit_price_toman
print(amount_toman)

# C05
print(8 / 2)
print(type(8 / 2))
print(8 // 3)
print(8 % 3)
print(-7 // 2)
print(int(-3.5))

# C06
item_count = 17
items_per_box = 6
full_boxes = item_count // items_per_box
remaining_items = item_count % items_per_box
print(full_boxes)
print(remaining_items)

# C07
print(2 + 3 * 4)
print((2 + 3) * 4)
print(-2 ** 2)
print((-2) ** 2)
print(2 ** 3 ** 2)
print((2 ** 3) ** 2)

# C08
initial_amount_toman = 720_000
refund_amount_toman = 240_000
refund_amount_ratio = refund_amount_toman / initial_amount_toman
refund_amount_percent = refund_amount_ratio * 100
print(round(refund_amount_ratio, 4))
print(round(refund_amount_percent, 2))

# C09
print(12 + 3)
print("12" + "3")
print("12" * 3)
print(type("12"))

# C10
customer_code = "00127"
print(customer_code)
print(int(customer_code))
print(len(customer_code))

# C11
raw_quantity = " 3 "
clean_quantity_text = raw_quantity.strip()
quantity = int(clean_quantity_text)
print(len(raw_quantity))
print(len(clean_quantity_text))
print(quantity * 240_000)

# C12
ordered_quantity = 3
returned_quantity = 1
has_return = returned_quantity > 0
return_within_order = returned_quantity <= ordered_quantity
print(has_return)
print(return_within_order)
print(3 == "3")
print(3 == 3.0)

# C13
ordered_quantity = 3
returned_quantity = 1
valid_return = (returned_quantity >= 0) and (returned_quantity <= ordered_quantity)
has_any_item = (ordered_quantity > 0) or (returned_quantity > 0)
print(valid_return)
print(has_any_item)
print(not valid_return)

# C14
shipping_cost_toman = None
print(shipping_cost_toman is None)
print(shipping_cost_toman is not None)
print(None == 0)
print(None == "")

# C15
quantity_text = "3"
price_text = "240000"
quantity = int(quantity_text)
unit_price_toman = int(price_text)
print(quantity * unit_price_toman)
print(float("3.5"))
print(str(240000) + " toman")
print(int(3.9))
print(bool("False"))
print(bool(""))

# C16
order_id = "O-0301"
amount_after_returns_toman = 480_000
print(f"سفارش {order_id}")
print(f"مبلغ پس از کسر مرجوعی: {amount_after_returns_toman:,} تومان")
print(type(amount_after_returns_toman))

# C17
refund_amount_ratio = 1 / 3
ratio_display = f"{refund_amount_ratio:.4f}"
percent_display = f"{refund_amount_ratio:.2%}"
print(ratio_display)
print(percent_display)
print(type(percent_display))
print(f"{refund_amount_ratio * 100:.2f} درصد")

# C18
result = 0.1 + 0.2
print(result)
print(result == 0.3)
print(f"{result:.2f}")
print(result)

# C19
import math

print(math.isclose(0.1 + 0.2, 0.3, rel_tol=1e-9, abs_tol=0.0))
print(math.isclose(1e-12, 0.0, rel_tol=1e-9, abs_tol=1e-10))

# C20
print(round(2.5))
print(round(3.5))
print(round(2.675, 2))

# C21
from decimal import Decimal, ROUND_HALF_UP

unit_price = Decimal("23.75")
tax_rate = Decimal("0.075")
amount_with_tax = unit_price * (Decimal("1") + tax_rate)
rounded_amount = amount_with_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print(amount_with_tax)
print(rounded_amount)

# C22
ordered_quantity = 3
returned_quantity = 1
unit_price_toman = 240_000
wrong_amount = ordered_quantity - returned_quantity * unit_price_toman
correct_amount = (ordered_quantity - returned_quantity) * unit_price_toman
print(wrong_amount)
print(correct_amount)

# C23
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

# C24
ordered_quantity = 3
returned_quantity = 1
unit_price_toman = 240_000
initial_amount_toman = ordered_quantity * unit_price_toman
refund_amount_toman = returned_quantity * unit_price_toman
remaining_quantity = ordered_quantity - returned_quantity
amount_after_returns_toman = initial_amount_toman - refund_amount_toman
print(initial_amount_toman == 720_000)
print(refund_amount_toman == 240_000)
print(amount_after_returns_toman == 480_000)
print(initial_amount_toman == refund_amount_toman + amount_after_returns_toman)
print(amount_after_returns_toman == remaining_quantity * unit_price_toman)
