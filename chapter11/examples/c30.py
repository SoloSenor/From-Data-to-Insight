import csv
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "orders.csv"
    path.write_text("quantity,price,returned\n3,100,1\n2,50,0\n", encoding="ascii")
    with path.open(encoding="ascii", newline="") as source:
        rows = csv.DictReader(source)
        total = sum((int(row["quantity"]) - int(row["returned"]))
                    * int(row["price"]) for row in rows)
    print(total)
    print(total == 300)
