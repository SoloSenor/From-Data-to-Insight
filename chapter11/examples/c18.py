def retained(quantity, price, returned):
    return (quantity - returned) * price

quantity, price, returned = 3, 100, 1
expected = 200
actual = retained(quantity, price, returned)
print(actual == expected)
