class Batch:
    def __init__(self, batch_id):
        self.batch_id = batch_id
        self.notes = []

first = Batch("B01")
second = Batch("B02")
first.notes.append("checked")
print(first.notes)
print(second.notes)
print(first.notes is second.notes)
