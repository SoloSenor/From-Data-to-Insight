"""Check notebook outputs in a fresh real Jupyter kernel."""
import json
from importlib.metadata import version
from pathlib import Path
import platform
import sys
import tempfile

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "notebooks/08-functions-and-modules.ipynb"
    original = path.read_bytes()
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    catalog = json.loads((ROOT / "examples/catalog.json").read_text(encoding="utf-8"))
    notebook.cells.append(nbformat.v4.new_code_cell(
        'import json, platform, sys\n'
        'print(json.dumps({"python": platform.python_version(), '
        '"executable": sys.executable, "platform": platform.platform()}))'))
    with tempfile.TemporaryDirectory(prefix="chapter08-kernel-") as directory:
        executed = NotebookClient(notebook, timeout=90, kernel_name="python3",
                                  allow_errors=False,
                                  resources={"metadata": {"path": directory}}).execute()
    cells = [cell for cell in executed.cells if cell.cell_type == "code"]
    assert len(cells) == 31
    for cell, item in zip(cells[:-1], catalog, strict=True):
        assert cell.source == item["code"]
        assert cell.execution_count is not None
        assert all(output.output_type == "stream" and output.name == "stdout"
                   for output in cell.outputs), item["id"]
        output = "".join(o.text for o in cell.outputs)
        assert output == item["output"], item["id"]
        assert cell.source.isascii() and output.isascii()
    kernel = json.loads("".join(o.text for o in cells[-1].outputs))
    assert path.read_bytes() == original
    print(json.dumps({"status": "PASS", "matched_teaching_code_cells": 30,
                      "extra_environment_probe_cells": 1, "kernel": kernel,
                      "runner_python": platform.python_version(),
                      "runner_executable": sys.executable,
                      "packages": {p: version(p) for p in
                                   ["nbformat", "nbclient", "jupyter_client", "ipykernel"]},
                      "published_notebook_unchanged": True,
                      "browser_tested": False}, indent=2))


if __name__ == "__main__":
    main()
