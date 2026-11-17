class Batch:
    def __init__(self, batch_id, tested):
        self.batch_id = batch_id
        self.tested = tested

first = Batch("B01", 80)
second = Batch("B02", 120)
print(first.batch_id, first.tested)
print(second.batch_id, second.tested)
print(first is second)
