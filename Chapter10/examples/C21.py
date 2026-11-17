from itertools import chain, count, islice
source = count(10, 2)
print(list(islice(source, 3)))
print(next(source))
print(list(chain([1, 2], [3], [])))
