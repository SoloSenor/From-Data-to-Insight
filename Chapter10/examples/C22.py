from itertools import groupby
values = ["A", "A", "B", "A"]
for key, group in groupby(values):
    print(key, list(group))
