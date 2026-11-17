def combined():
    yield "header"
    yield from [10, 20]
    yield from (value * 2 for value in [3, 4])

print(list(combined()))
