# -*- coding: utf-8 -*-
"""Optional interactive example; not part of the unattended notebook.

Assumes a valid integer quantity. Domain validation is introduced later.
All values are synthetic; the price is in toman.
"""
quantity_text = input("تعداد کالا: ")
quantity = int(quantity_text)
unit_price_toman = 240_000
print(quantity * unit_price_toman)
