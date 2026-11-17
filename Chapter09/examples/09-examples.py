"""Run 30 independent, ASCII-only chapter 09 examples."""

# Example 09-01
from pathlib import Path
path = Path("data") / "raw" / "orders.csv"
print(path.as_posix())
print(path.name, path.stem, path.suffix)
print(path.parent.as_posix())

# Example 09-02
from pathlib import Path
print(Path.cwd().is_absolute())
print(Path("data/orders.csv").is_absolute())

# Example 09-03
from pathlib import PureWindowsPath
path = PureWindowsPath(r"C:\book\data\orders.csv")
print(path.name)
print(path.drive)
print(path.as_posix())

# Example 09-04
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    output = Path(folder) / "outputs" / "daily"
    output.mkdir(parents=True, exist_ok=True)
    print(output.exists(), output.is_dir(), output.is_file())
print(output.exists())

# Example 09-05
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    root = Path(folder)
    for name in ["b.csv", "a.csv", "notes.txt"]:
        (root / name).write_text("sample", encoding="utf-8")
    names = sorted(path.name for path in root.glob("*.csv")
                   if path.is_file())
    print(names)

# Example 09-06
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "note.txt"
    count = path.write_text("alpha\nbeta\n", encoding="utf-8")
    print(count)
    print(repr(path.read_text(encoding="utf-8")))

# Example 09-07
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "note.txt"
    with path.open("x", encoding="utf-8") as target:
        target.write("ready")
        print(target.closed)
    print(target.closed)

# Example 09-08
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "note.txt"
    with path.open("x", encoding="utf-8", newline="\n") as target:
        count = target.write("A")
        print("B", file=target)
    print(count)
    print(repr(path.read_text(encoding="utf-8")))

# Example 09-09
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "events.txt"
    path.write_text("start\n", encoding="utf-8")
    with path.open("a", encoding="utf-8", newline="\n") as target:
        target.write("finish\n")
    print(path.read_text(encoding="utf-8").splitlines())

# Example 09-10
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "result.txt"
    with path.open("x", encoding="utf-8") as target:
        target.write("approved")
    print(path.read_text(encoding="utf-8"))

# Example 09-11
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "letters.txt"
    path.write_text("ABCD", encoding="utf-8")
    with path.open("r", encoding="utf-8") as source:
        print(source.read(2))
        print(source.read())
        print(repr(source.read()))
        source.seek(0)
        print(source.read(1))

# Example 09-12
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "lines.txt"
    path.write_text("  A  \n\nB\n", encoding="utf-8")
    with path.open("r", encoding="utf-8") as source:
        for number, line in enumerate(source, start=1):
            print(number, repr(line.rstrip("\n")))

# Example 09-13
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "lines.txt"
    path.write_text("\n", encoding="utf-8")
    with path.open("r", encoding="utf-8") as source:
        print(repr(source.readline()))
        print(repr(source.readline()))

# Example 09-14
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "lines.txt"
    path.write_bytes(b"A\r\nB\r\n")
    print(repr(path.read_bytes()))
    print(repr(path.read_text(encoding="utf-8")))

# Example 09-15
text = "\u00e9"
encoded = text.encode("utf-8")
print(len(text), len(encoded))
print(list(encoded))
print(encoded.decode("utf-8") == text)

# Example 09-16
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    path = Path(folder) / "header.txt"
    path.write_bytes(b"\xef\xbb\xbforder_id\n")
    plain = path.read_text(encoding="utf-8")
    clean = path.read_text(encoding="utf-8-sig")
    print(plain.startswith("\ufeff"))
    print(clean.splitlines()[0])

# Example 09-17
import csv
from io import StringIO
text = 'order_id,category,quantity\nA01,"Books, Stationery",2\n'
with StringIO(text, newline="") as source:
    rows = list(csv.reader(source))
print(rows[1])

# Example 09-18
line = 'A01,"Books, Stationery",2'
print(line.split(","))

# Example 09-19
import csv
from io import StringIO
text = "order_id,quantity\n0012,3\n"
with StringIO(text, newline="") as source:
    row = next(csv.DictReader(source))
print(row["order_id"], type(row["order_id"]).__name__)
print(row["quantity"], type(row["quantity"]).__name__)

# Example 09-20
import csv
from io import StringIO
text = "order_id,quantity,unit_price_toman\n0012,3,100\n"
with StringIO(text, newline="") as source:
    row = next(csv.DictReader(source))
for field in ["quantity", "unit_price_toman"]:
    row[field] = int(row[field])
print(row["order_id"])
print(row["quantity"] * row["unit_price_toman"])

# Example 09-21
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
rows = [{"order_id": "A01", "category": 'Tools, "Small"'},
        {"order_id": "A02", "category": "Line1\nLine2"}]
with TemporaryDirectory() as folder:
    path = Path(folder) / "items.csv"
    with path.open("x", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["order_id", "category"],
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with path.open("r", encoding="utf-8", newline="") as source:
        restored = list(csv.DictReader(source))
    print(restored == rows)
    print(len(restored), len(path.read_text(encoding="utf-8").splitlines()))

# Example 09-22
import csv
from io import StringIO
text = "order_id;quantity\nA01;2\n"
with StringIO(text, newline="") as source:
    row = next(csv.DictReader(source, delimiter=";"))
print(row["order_id"], int(row["quantity"]))

# Example 09-23
import csv
from io import StringIO
text = "order_id,quantity\nA01,\nA02\n"
with StringIO(text, newline="") as source:
    rows = list(csv.DictReader(source))
print(repr(rows[0]["quantity"]))
print(rows[1]["quantity"] is None)

# Example 09-24
import json
text = '{"quantity": 2, "approved": true, "note": null}'
row = json.loads(text)
print(row["quantity"], type(row["quantity"]).__name__)
print(row["approved"], row["note"])

# Example 09-25
import json
row = {"order_id": "0012", "quantity": 2, "note": None}
text = json.dumps(row, ensure_ascii=True, sort_keys=True,
                  allow_nan=False)
print(text)
print(json.loads(text) == row)

# Example 09-26
import json
from pathlib import Path
from tempfile import TemporaryDirectory
rows = [{"order_id": "A01", "quantity": 2}]
with TemporaryDirectory() as folder:
    path = Path(folder) / "orders.json"
    with path.open("x", encoding="utf-8", newline="\n") as target:
        json.dump(rows, target, indent=2, ensure_ascii=True,
                  allow_nan=False)
        target.write("\n")
    with path.open("r", encoding="utf-8") as source:
        restored = json.load(source)
    print(restored == rows)

# Example 09-27
import json
original = {1: ("A", "B")}
restored = json.loads(json.dumps(original))
print(restored)
print(restored == original)

# Example 09-28
import json
row = json.loads('{"quantity": 2, "quantity": 9}')
print(row["quantity"])

# Example 09-29
import csv
import json
from io import StringIO
csv_text = "order_id,quantity\n0012,2\n"
json_text = '[{"order_id": "0012", "quantity": 2}]'
with StringIO(csv_text, newline="") as source:
    csv_rows = list(csv.DictReader(source))
json_rows = json.loads(json_text)
print(csv_rows == json_rows)
csv_rows[0]["quantity"] = int(csv_rows[0]["quantity"])
print(csv_rows == json_rows)

# Example 09-30
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
rows = [
    {"order_id": "0012", "quantity": 2,
     "unit_price_toman": 100, "returned_quantity": 1},
    {"order_id": "0013", "quantity": 3,
     "unit_price_toman": 50, "returned_quantity": 0},
]
with TemporaryDirectory() as folder:
    root = Path(folder)
    path = root / "orders.csv"
    with path.open("x", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]),
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with path.open("r", encoding="utf-8", newline="") as source:
        loaded = list(csv.DictReader(source))
    for row in loaded:
        for field in ["quantity", "unit_price_toman", "returned_quantity"]:
            row[field] = int(row[field])
    gross = sum(row["quantity"] * row["unit_price_toman"]
                for row in loaded)
    refund = sum(row["returned_quantity"] * row["unit_price_toman"]
                 for row in loaded)
    result = {"gross_toman": gross, "refund_toman": refund,
              "retained_toman": gross - refund}
    output = root / "report.json"
    with output.open("x", encoding="utf-8") as target:
        json.dump(result, target, allow_nan=False)
    with output.open("r", encoding="utf-8") as source:
        restored = json.load(source)
    print(gross, refund, gross - refund)
    print(restored == result)
