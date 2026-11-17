from itertools import groupby
from operator import itemgetter
rows = [("B", 3), ("A", 2), ("A", 5)]
key = itemgetter(0)
for category, group in groupby(sorted(rows, key=key), key=key):
    print(category, sum(row[1] for row in group))
