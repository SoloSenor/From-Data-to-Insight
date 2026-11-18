def total(rows):
    return sum((q - r) * p for q, p, r in rows)

rows = [(3, 100, 1), (2, 50, 0)]
scaled = [(q, 2 * p, r) for q, p, r in rows]
print(total(rows) == total(list(reversed(rows))))
print(total(scaled) == 2 * total(rows))
