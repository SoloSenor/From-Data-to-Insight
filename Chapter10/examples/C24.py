from itertools import islice

def chunks(values, size):
    if type(size) is not int or size <= 0:
        raise ValueError("size must be a positive integer")
    source = iter(values)
    while True:
        batch = tuple(islice(source, size))
        if not batch:
            return
        yield batch

print(list(chunks(range(7), 3)))
