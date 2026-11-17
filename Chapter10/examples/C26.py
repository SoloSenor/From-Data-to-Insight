class Batch:
    def __init__(self, tested, rejected):
        self.tested = tested
        self.rejected = rejected

    def rejection_rate(self):
        if self.tested == 0:
            return None
        return self.rejected / self.tested

batch = Batch(80, 4)
print(batch.rejection_rate())
print(Batch.rejection_rate(batch))
print(Batch(0, 0).rejection_rate())
