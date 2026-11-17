values = [10, 20, 30]
left = iter(values)
right = iter(values)
print(next(left), next(left), next(right))
print(list(left))
print(values)
