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
for key in quote:
    print(key, quote[key])
