def retained(quantity, price, returned):
    return (quantity - returned) * price

print(retained(3, 100, 1))
print(retained(3, 100, 0))
print(retained(3, 100, 3))
