values = [2, 4, 6]
eager = [value * 2 for value in values]
lazy = (value * 2 for value in values)
print(type(eager).__name__, type(lazy).__name__)
print(sum(lazy), sum(lazy))
print(sum(eager), sum(eager))
