values = [1, 2, 3, 4]
selected = filter(lambda value: value % 2 == 0, values)
scaled = map(lambda value: value * 10, selected)
print(next(scaled))
print(list(scaled))
print(list(scaled))
