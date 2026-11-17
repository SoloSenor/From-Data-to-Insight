def summarize(values):
    count = 0
    total = 0
    for value in values:
        count += 1
        total += value
    average = total / count if count else None
    return count, total, average

source = (value for value in [10, 20, 30])
print(summarize(source))
print(summarize(source))
print(summarize([]))
