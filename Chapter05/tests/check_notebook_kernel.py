"""Run and verify the teaching notebook in a fresh real Jupyter kernel."""
import json
from pathlib import Path
import platform
import sys
from importlib.metadata import version

import nbformat
from nbclient import NotebookClient

from test_chapter05 import BY_ID, ROOT


def main():
    path = ROOT / 'notebooks/05-control-flow-functions.ipynb'
    before = path.read_bytes()
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    notebook.cells.append(nbformat.v4.new_code_cell(
        'import json, platform, sys\n'
        'print(json.dumps({"python": platform.python_version(), '
        '"executable": sys.executable, "platform": platform.platform()}))\n'))
    executed = NotebookClient(notebook, timeout=90, kernel_name='python3',
                              allow_errors=False, resources={'metadata': {'path': str(ROOT)}}).execute()
    code_cells = [cell for cell in executed.cells if cell.cell_type == 'code']
    assert len(code_cells) == 26
    for index, cell in enumerate(code_cells[:-1], 1):
        name = f'C{index:02}'
        assert cell.metadata['example_id'] == name, name
        assert cell.source == BY_ID[name]['code'], name
        assert all(o.output_type == 'stream' and o.name == 'stdout'
                   for o in cell.outputs), name
        output = ''.join(o.text for o in cell.outputs)
        assert output == BY_ID[name]['output'], name
        assert output.isascii(), name
        assert cell.execution_count is not None, name
    probe = json.loads(''.join(o.text for o in code_cells[-1].outputs))
    assert path.read_bytes() == before, 'Published notebook was modified'
    result = {
        'status': 'PASS',
        'matched_teaching_code_cells': 25,
        'kernel': probe,
        'runner_python': platform.python_version(),
        'runner_executable': sys.executable,
        'packages': {name: version(name) for name in
                     ('nbformat', 'nbclient', 'jupyter_client', 'ipykernel')},
        'published_notebook_unchanged': True,
        'browser_tested': False,
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
