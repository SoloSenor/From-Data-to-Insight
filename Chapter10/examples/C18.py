from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

def iter_lines(path):
    with path.open(encoding="utf-8") as source:
        for line in source:
            yield line.rstrip("\n")

with TemporaryDirectory() as folder:
    path = Path(folder) / "values.txt"
    path.write_text("first\nsecond\n", encoding="utf-8")
    with closing(iter_lines(path)) as lines:
        print(next(lines))
    print(list(lines))
