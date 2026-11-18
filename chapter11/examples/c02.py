actions = [lambda: int("two"), lambda: 1 / 0, lambda: {}["price"]]
for action in actions:
    try:
        action()
    except (ValueError, ZeroDivisionError, KeyError) as exc:
        print(type(exc).__name__)
