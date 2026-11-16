"""Optional real-kernel QA; nbformat, nbclient and a python3 kernel are required.

Run from the chapter directory:
    python tests/check_notebook_kernel.py

This script does not start the browser interface or change the published notebook.
"""
from pathlib import Path
import re

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'notebooks/03-values-variables-calculation.ipynb'
notebook = nbformat.read(NOTEBOOK, as_version=4)
nbformat.validate(notebook)
notebook.cells.insert(0, nbformat.v4.new_code_cell('import sys; print(sys.version); print(sys.executable)'))
client = NotebookClient(
    notebook,
    timeout=25,
    startup_timeout=25,
    kernel_name='python3',
    resources={'metadata': {'path': str(ROOT)}},
)
client.execute()
text = (ROOT / 'chapter-03-full-fa.txt').read_text(encoding='utf-8')
expected = re.findall(r'\[کد (C\d+)\]\n```python\n(.*?)\n```\n\[خروجی \1\]\n```text\n(.*?)\n```', text, re.S)
code_cells = [cell for cell in notebook.cells[1:] if cell.cell_type == 'code']
if len(code_cells) != 24 or len(expected) != 24:
    raise AssertionError('Expected 24 chapter code cells.')
for (case_id, source, reference), cell in zip(expected, code_cells, strict=True):
    if cell.source != source:
        raise AssertionError(f'{case_id}: notebook source differs from chapter.')
    actual = ''.join(output.get('text', '') for output in cell.outputs if output.output_type == 'stream').rstrip('\n')
    if actual != reference:
        raise AssertionError(f'{case_id}: output differs from chapter.')
print('PASS: notebook schema and 24 cell outputs through a fresh real Jupyter kernel.')
print('Kernel runtime:')
print(''.join(output.get('text', '') for output in notebook.cells[0].outputs), end='')
print('Published notebook unchanged; no browser UI was tested.')
