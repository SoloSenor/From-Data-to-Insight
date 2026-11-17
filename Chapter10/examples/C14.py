def steps():
    print("started")
    yield 10
    print("resumed")
    yield 20

source = steps()
print("created")
print(next(source))
print(next(source))
