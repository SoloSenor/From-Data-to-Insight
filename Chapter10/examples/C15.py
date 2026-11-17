def until_negative(values):
    for value in values:
        if value < 0:
            return
        yield value

print(list(until_negative([3, 0, -1, 9])))
print(list(until_negative([])))
