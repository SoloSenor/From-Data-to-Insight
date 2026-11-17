"""Execute the released notebook in a fresh real Jupyter kernel."""
import json
from pathlib import Path
import platform
import shutil
import sys
import tempfile
from importlib.metadata import version

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "notebooks/06-first-end-to-end-analysis.ipynb"
    before = path.read_bytes()
    catalog = json.loads((ROOT / "examples/catalog.json").read_text())
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    notebook.cells.append(nbformat.v4.new_code_cell(
        'import json, platform, sys\n'
        'from importlib.metadata import version\n'
        'print(json.dumps({"python": platform.python_version(), '
        '"executable": sys.executable, "platform": platform.platform(), '
        '"packages": {p: version(p) for p in '
        '["numpy", "pandas", "matplotlib"]}}))'))
    with tempfile.TemporaryDirectory(prefix="chapter06-kernel-") as directory:
        temporary = Path(directory)
        shutil.copytree(ROOT / "data", temporary / "data")
        executed = NotebookClient(
            notebook, timeout=90, kernel_name="python3", allow_errors=False,
            resources={"metadata": {"path": str(temporary)}}).execute()
        cells = [cell for cell in executed.cells if cell.cell_type == "code"]
        assert len(cells) == 25
        for cell, item in zip(cells[:-1], catalog):
            assert cell.metadata["example_id"] == item["id"]
            assert cell.source == item["code"].rstrip()
            assert cell.execution_count is not None
            assert all(out.output_type == "stream" and out.name == "stdout"
                       for out in cell.outputs), item["id"]
            output = ''.join(out.text for out in cell.outputs)
            assert output == item["output"], item["id"]
            assert output.isascii(), item["id"]
        import pandas as pd
        csv_path = temporary / "outputs/category-summary.csv"
        summary = pd.read_csv(csv_path, index_col="category")
        assert summary["retained_toman"].to_dict() == {
            "Digital": 2450000, "Books": 690000, "Stationery": 450000}
        png = (temporary / "outputs/category-retained.png").read_bytes()
        assert png.startswith(b"\x89PNG\r\n\x1a\n")
    probe = json.loads(''.join(out.text for out in cells[-1].outputs))
    assert path.read_bytes() == before
    result = {
        "status": "PASS", "matched_teaching_code_cells": 24,
        "extra_environment_probe_cells": 1,
        "kernel": probe,
        "runner_python": platform.python_version(),
        "runner_executable": sys.executable,
        "packages": {p: version(p) for p in
                     ["nbformat", "nbclient", "jupyter_client", "ipykernel"]},
        "csv_and_png_artifacts_checked": True,
        "published_notebook_unchanged": True,
        "browser_tested": False,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
