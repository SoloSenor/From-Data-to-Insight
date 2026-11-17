from dataclasses import dataclass

@dataclass(frozen=True)
class Amount:
    gross: int
    refund: int

    def retained(self):
        return self.gross - self.refund

amount = Amount(500, 120)
print(amount)
print(amount.retained())
print(amount == Amount(500, 120))
