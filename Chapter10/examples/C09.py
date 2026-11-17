ids = ["B01", "B02"]
counts = [4, 6]
for position, (batch_id, count) in enumerate(
        zip(ids, counts, strict=True), start=1):
    print(position, batch_id, count)
