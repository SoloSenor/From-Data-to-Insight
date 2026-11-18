def require_quantity(value):
    if type(value) is not int:
        raise TypeError("quantity must be an integer")
    if value <= 0:
        raise ValueError("quantity must be positive")
    return value

for value in (3, 0, True):
    try:
        print(require_quantity(value))
    except (TypeError, ValueError) as exc:
        print(type(exc).__name__)
