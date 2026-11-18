def wrong_retained(quantity, price, returned):
    return quantity * price - returned

actual = wrong_retained(3, 100, 1)
print(actual)
print(actual == 200)
