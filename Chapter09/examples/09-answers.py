"""Run chapter 09 coding answers in order."""

# Exercise 5
from pathlib import Path
from tempfile import TemporaryDirectory

def count_nonblank(path):
    count = 0
    with Path(path).open("r", encoding="utf-8") as source:
        for line in source:
            if line.strip():
                count += 1
    return count

with TemporaryDirectory() as folder:
    path = Path(folder) / "lines.txt"
    path.write_text("alpha\n\n   \nbeta\n", encoding="utf-8")
    print(count_nonblank(path))

# Exercise 6
import csv
from io import StringIO
text = "order_id,quantity,unit_price_toman\n0012,3,100\n"
with StringIO(text, newline="") as source:
    row = next(csv.DictReader(source))
amount = int(row["quantity"]) * int(row["unit_price_toman"])
print(row["order_id"], amount)

# Exercise 7
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
rows = [{"category": "A,B"}, {"category": "C\nD"}]
with TemporaryDirectory() as folder:
    path = Path(folder) / "quoted.csv"
    with path.open("x", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["category"],
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with path.open("r", encoding="utf-8", newline="") as source:
        restored = list(csv.DictReader(source))
    print(restored == rows)

# Exercise 8
import json
row = {"quantity": 2, "order_id": "0012"}
text = json.dumps(row, sort_keys=True, allow_nan=False)
print(text)
print(json.loads(text) == row)

# Exercise 9
from pathlib import Path
from tempfile import TemporaryDirectory

def write_once(path, text):
    with Path(path).open("x", encoding="utf-8") as target:
        target.write(text)

with TemporaryDirectory() as folder:
    path = Path(folder) / "result.txt"
    write_once(path, "saved")
    print(path.read_text(encoding="utf-8"))

# Exercise 10
import json
try:
    json.dumps({"rate": float("nan")}, allow_nan=False)
except ValueError:
    print("rejected")

# Exercise 11
def valid_counts(quantity, returned):
    return (type(quantity) is int and type(returned) is int
            and quantity > 0 and 0 <= returned <= quantity)

print(valid_counts(3, 1))
print(valid_counts(True, 0))
print(valid_counts(2, 3))

# Exercise 12
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
rows = [{"batch_id": "B01", "tested": 40, "defects": 2},
        {"batch_id": "B02", "tested": 60, "defects": 3}]
with TemporaryDirectory() as folder:
    root = Path(folder)
    with (root / "batches.csv").open(
            "x", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]),
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with (root / "batches.csv").open(
            "r", encoding="utf-8", newline="") as source:
        loaded = list(csv.DictReader(source))
    tested = sum(int(row["tested"]) for row in loaded)
    defects = sum(int(row["defects"]) for row in loaded)
    result = {"tested": tested, "defects": defects,
              "defect_rate": defects / tested if tested else None}
    with (root / "quality.json").open("x", encoding="utf-8") as target:
        json.dump(result, target, allow_nan=False)
    with (root / "quality.json").open("r", encoding="utf-8") as source:
        restored = json.load(source)
    print(tested, defects, f"{result['defect_rate']:.2%}")
    print(restored == result)
