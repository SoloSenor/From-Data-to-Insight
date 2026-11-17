"""Independent teaching examples, executed in fresh namespaces."""

# BEGIN C01
exec(compile('import math\nprint(math.isqrt(81))\nprint(math.isclose(0.1 + 0.2, 0.3))\n', "C01", "exec"), {})
# END C01

# BEGIN C02
exec(compile('from statistics import mean, median\nvalues = [10, 12, 14, 100]\nprint(mean(values))\nprint(median(values))\n', "C02", "exec"), {})
# END C02

# BEGIN C03
exec(compile('from datetime import date, timedelta\nstart = date.fromisoformat("2024-02-28")\nend = date.fromisoformat("2024-03-01")\nprint((end - start).days)\nprint((start + timedelta(days=2)).isoformat())\n', "C03", "exec"), {})
# END C03

# BEGIN C04
exec(compile('from decimal import Decimal\nprint(0.1 + 0.2 == 0.3)\nprint(Decimal("0.1") + Decimal("0.2"))\nprint(Decimal("12.345").quantize(Decimal("0.01")))\n', "C04", "exec"), {})
# END C04

# BEGIN C05
exec(compile('values = [10, 20, 30]\nleft = iter(values)\nright = iter(values)\nprint(next(left), next(left), next(right))\nprint(list(left))\nprint(values)\n', "C05", "exec"), {})
# END C05

# BEGIN C06
exec(compile('source = iter([2, 3, 5])\nprint(iter(source) is source)\nprint(sum(source))\nprint(sum(source))\n', "C06", "exec"), {})
# END C06

# BEGIN C07
exec(compile('values = range(2, 8, 2)\nprint(type(values).__name__)\nprint(values[1], len(values))\nprint(list(values))\nprint(list(values))\nprint(iter(values) is values)\n', "C07", "exec"), {})
# END C07

# BEGIN C08
exec(compile('source = iter([None, 7])\nmissing = object()\nprint(next(source, missing) is None)\nprint(next(source, missing))\nprint(next(source, missing) is missing)\n', "C08", "exec"), {})
# END C08

# BEGIN C09
exec(compile('ids = ["B01", "B02"]\ncounts = [4, 6]\nfor position, (batch_id, count) in enumerate(\n        zip(ids, counts, strict=True), start=1):\n    print(position, batch_id, count)\n', "C09", "exec"), {})
# END C09

# BEGIN C10
exec(compile('source = (value for value in [30, 10, 20])\nordered = sorted(source)\nprint(ordered)\nprint(list(source))\nprint(type(ordered).__name__)\n', "C10", "exec"), {})
# END C10

# BEGIN C11
exec(compile('source = iter([0, 0, 5, 8])\nprint(any(source))\nprint(list(source))\nprint(all([]), any([]))\n', "C11", "exec"), {})
# END C11

# BEGIN C12
exec(compile('values = [1, 2, 3, 4]\nselected = filter(lambda value: value % 2 == 0, values)\nscaled = map(lambda value: value * 10, selected)\nprint(next(scaled))\nprint(list(scaled))\nprint(list(scaled))\n', "C12", "exec"), {})
# END C12

# BEGIN C13
exec(compile('values = [2, 4, 6]\neager = [value * 2 for value in values]\nlazy = (value * 2 for value in values)\nprint(type(eager).__name__, type(lazy).__name__)\nprint(sum(lazy), sum(lazy))\nprint(sum(eager), sum(eager))\n', "C13", "exec"), {})
# END C13

# BEGIN C14
exec(compile('def steps():\n    print("started")\n    yield 10\n    print("resumed")\n    yield 20\n\nsource = steps()\nprint("created")\nprint(next(source))\nprint(next(source))\n', "C14", "exec"), {})
# END C14

# BEGIN C15
exec(compile('def until_negative(values):\n    for value in values:\n        if value < 0:\n            return\n        yield value\n\nprint(list(until_negative([3, 0, -1, 9])))\nprint(list(until_negative([])))\n', "C15", "exec"), {})
# END C15

# BEGIN C16
exec(compile('def combined():\n    yield "header"\n    yield from [10, 20]\n    yield from (value * 2 for value in [3, 4])\n\nprint(list(combined()))\n', "C16", "exec"), {})
# END C16

# BEGIN C17
exec(compile('factor = 2\nvalues = [1, 2]\nsource = (factor * value for value in values)\nfactor = 10\nprint(list(source))\n', "C17", "exec"), {})
# END C17

# BEGIN C18
exec(compile('from contextlib import closing\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\n\ndef iter_lines(path):\n    with path.open(encoding="utf-8") as source:\n        for line in source:\n            yield line.rstrip("\\n")\n\nwith TemporaryDirectory() as folder:\n    path = Path(folder) / "values.txt"\n    path.write_text("first\\nsecond\\n", encoding="utf-8")\n    with closing(iter_lines(path)) as lines:\n        print(next(lines))\n    print(list(lines))\n', "C18", "exec"), {})
# END C18

# BEGIN C19
exec(compile('from collections import Counter\ncategories = ["Books", "Digital", "Books", "Stationery"]\ncounts = Counter(categories)\nprint(sorted(counts.items()))\nprint(counts["Missing"])\nprint("Missing" in counts)\n', "C19", "exec"), {})
# END C19

# BEGIN C20
exec(compile('from collections import defaultdict\ntotals = defaultdict(int)\nprint(totals.get("Books"))\nprint("Books" in totals)\nprint(totals["Books"])\nprint("Books" in totals)\ntotals["Books"] += 120\nprint(dict(totals))\n', "C20", "exec"), {})
# END C20

# BEGIN C21
exec(compile('from itertools import chain, count, islice\nsource = count(10, 2)\nprint(list(islice(source, 3)))\nprint(next(source))\nprint(list(chain([1, 2], [3], [])))\n', "C21", "exec"), {})
# END C21

# BEGIN C22
exec(compile('from itertools import groupby\nvalues = ["A", "A", "B", "A"]\nfor key, group in groupby(values):\n    print(key, list(group))\n', "C22", "exec"), {})
# END C22

# BEGIN C23
exec(compile('from itertools import groupby\nfrom operator import itemgetter\nrows = [("B", 3), ("A", 2), ("A", 5)]\nkey = itemgetter(0)\nfor category, group in groupby(sorted(rows, key=key), key=key):\n    print(category, sum(row[1] for row in group))\n', "C23", "exec"), {})
# END C23

# BEGIN C24
exec(compile('from itertools import islice\n\ndef chunks(values, size):\n    if type(size) is not int or size <= 0:\n        raise ValueError("size must be a positive integer")\n    source = iter(values)\n    while True:\n        batch = tuple(islice(source, size))\n        if not batch:\n            return\n        yield batch\n\nprint(list(chunks(range(7), 3)))\n', "C24", "exec"), {})
# END C24

# BEGIN C25
exec(compile('class Batch:\n    def __init__(self, batch_id, tested):\n        self.batch_id = batch_id\n        self.tested = tested\n\nfirst = Batch("B01", 80)\nsecond = Batch("B02", 120)\nprint(first.batch_id, first.tested)\nprint(second.batch_id, second.tested)\nprint(first is second)\n', "C25", "exec"), {})
# END C25

# BEGIN C26
exec(compile('class Batch:\n    def __init__(self, tested, rejected):\n        self.tested = tested\n        self.rejected = rejected\n\n    def rejection_rate(self):\n        if self.tested == 0:\n            return None\n        return self.rejected / self.tested\n\nbatch = Batch(80, 4)\nprint(batch.rejection_rate())\nprint(Batch.rejection_rate(batch))\nprint(Batch(0, 0).rejection_rate())\n', "C26", "exec"), {})
# END C26

# BEGIN C27
exec(compile('class Batch:\n    def __init__(self, batch_id):\n        self.batch_id = batch_id\n        self.notes = []\n\nfirst = Batch("B01")\nsecond = Batch("B02")\nfirst.notes.append("checked")\nprint(first.notes)\nprint(second.notes)\nprint(first.notes is second.notes)\n', "C27", "exec"), {})
# END C27

# BEGIN C28
exec(compile('class Reading:\n    def __init__(self, value):\n        self.value = value\n\noriginal = Reading(12)\nalias = original\nindependent = Reading(original.value)\nalias.value = 15\nprint(original.value, independent.value)\nprint(alias is original)\n', "C28", "exec"), {})
# END C28

# BEGIN C29
exec(compile('from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Amount:\n    gross: int\n    refund: int\n\n    def retained(self):\n        return self.gross - self.refund\n\namount = Amount(500, 120)\nprint(amount)\nprint(amount.retained())\nprint(amount == Amount(500, 120))\n', "C29", "exec"), {})
# END C29

# BEGIN C30
exec(compile('def summarize(values):\n    count = 0\n    total = 0\n    for value in values:\n        count += 1\n        total += value\n    average = total / count if count else None\n    return count, total, average\n\nsource = (value for value in [10, 20, 30])\nprint(summarize(source))\nprint(summarize(source))\nprint(summarize([]))\n', "C30", "exec"), {})
# END C30
