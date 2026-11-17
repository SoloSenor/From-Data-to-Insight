"""Reference solutions; run from the chapter root."""

# BEGIN P01
exec(compile('import statistics\nvalues = [4, 6, 20]\nprint(statistics.mean(values))\nprint(statistics.median(values))\n', "P01", "exec"), {})
# END P01

# BEGIN P02
exec(compile('def summarize_nonnegative(values):\n    count = 0\n    total = 0\n    for value in values:\n        if value >= 0:\n            count += 1\n            total += value\n    return count, total\n\nprint(summarize_nonnegative(iter([3, -2, 0, 5])))\nprint(summarize_nonnegative(iter([])))\n', "P02", "exec"), {})
# END P02

# BEGIN P03
exec(compile('from itertools import islice\nsource = iter([10, 20, 30, 40])\nprint(list(islice(source, 2)))\nprint(list(source))\n', "P03", "exec"), {})
# END P03

# BEGIN P04
exec(compile('def scale(values, factor):\n    for value in values:\n        yield value * factor\n\nprint(list(scale([1, 2, 3], 10)))\nprint(list(scale([], 10)))\n', "P04", "exec"), {})
# END P04

# BEGIN P05
exec(compile('from itertools import islice\n\ndef chunks(values, size):\n    if type(size) is not int or size <= 0:\n        raise ValueError("size must be a positive integer")\n    def generate():\n        source = iter(values)\n        while True:\n            batch = tuple(islice(source, size))\n            if not batch:\n                return\n            yield batch\n    return generate()\n\nprint(list(chunks(range(5), 2)))\ntry:\n    chunks([], 0)\nexcept ValueError:\n    print("rejected at call")\n', "P05", "exec"), {})
# END P05

# BEGIN P06
exec(compile('from collections import Counter\nfrom itertools import groupby\nvalues = ["A", "B", "A"]\nprint([(key, len(list(group))) for key, group in groupby(values)])\nprint(sorted(Counter(values).items()))\n', "P06", "exec"), {})
# END P06

# BEGIN P07
exec(compile('from collections import defaultdict\n\ndef totals_by_category(rows):\n    totals = defaultdict(int)\n    for category, amount in rows:\n        totals[category] += amount\n    return sorted(totals.items())\n\nprint(totals_by_category(iter([("B", 5), ("A", 2), ("B", 3)])))\n', "P07", "exec"), {})
# END P07

# BEGIN P08
exec(compile('class Notebook:\n    def __init__(self, name):\n        self.name = name\n        self.notes = []\n\nfirst = Notebook("first")\nsecond = Notebook("second")\nfirst.notes.append("checked")\nprint(first.notes)\nprint(second.notes)\n', "P08", "exec"), {})
# END P08

# BEGIN P09
exec(compile('class Batch:\n    def __init__(self, tested, rejected):\n        if type(tested) is not int or type(rejected) is not int:\n            raise ValueError("counts must be integers")\n        if not 0 <= rejected <= tested:\n            raise ValueError("invalid counts")\n        self.tested = tested\n        self.rejected = rejected\n\n    def rejection_rate(self):\n        return self.rejected / self.tested if self.tested else None\n\nprint(Batch(100, 3).rejection_rate())\nprint(Batch(0, 0).rejection_rate())\n', "P09", "exec"), {})
# END P09

# BEGIN P10
exec(compile('from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Amount:\n    gross: int\n    refund: int\n\n    def retained(self):\n        return self.gross - self.refund\n\nprint(Amount(1200, 200).retained())\n', "P10", "exec"), {})
# END P10

# BEGIN P11
exec(compile('from contextlib import closing\nfrom pathlib import Path\nfrom order_report.source import iter_orders_csv\nfrom order_report.pipeline import summarize_orders\n\nwith closing(iter_orders_csv(Path("data") / "orders.csv")) as rows:\n    report = summarize_orders(rows)\nprint(report["orders"])\nprint(report["retained_toman"])\n', "P11", "exec"), {})
# END P11

# BEGIN P12
exec(compile('import json\nfrom contextlib import closing\nfrom pathlib import Path\nfrom order_report.source import iter_orders_csv\nfrom order_report.pipeline import summarize_orders\n\nexpected_rows = json.loads(Path("data/orders.json").read_text(encoding="utf-8"))\nwith closing(iter_orders_csv("data/orders.csv")) as rows:\n    actual_rows = list(rows)\nprint(actual_rows == expected_rows)\nprint(summarize_orders(iter(actual_rows)) == summarize_orders(iter(expected_rows)))\n', "P12", "exec"), {})
# END P12
