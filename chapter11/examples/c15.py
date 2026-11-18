from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "sample.txt"
    path.write_text("ready", encoding="ascii")
    try:
        with path.open(encoding="ascii") as source:
            raise ValueError("stop reading")
    except ValueError:
        print(source.closed)
