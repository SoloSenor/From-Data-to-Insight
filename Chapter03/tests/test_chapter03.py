"""Editorial tests; implementation details are not prerequisites for Chapter 03.

Run from the chapter directory:
    python -m unittest discover -s tests -v

Only the Python standard library is required.
"""
import ast
import builtins
from contextlib import redirect_stdout
import io
import json
import math
from pathlib import Path
import re
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / 'chapter-03-full-fa.txt').read_text(encoding='utf-8')
NORMAL = re.findall(r'\[کد ([CA]\d+)\]\n```python\n(.*?)\n```\n\[خروجی \1\]\n```text\n(.*?)\n```', TEXT, re.S)
ERRORS = re.findall(r'\[کد (E\d+) — خطای عمدی: (\w+)\]\n```python\n(.*?)\n```', TEXT, re.S)
BY_ID = {cid: (code, output) for cid, code, output in NORMAL}
REPORT = ROOT / 'examples/03-order-report.py'


def execute(source, filename='<chapter-example>'):
    namespace = {'__name__': '__main__'}
    output = io.StringIO()
    with redirect_stdout(output):
        exec(compile(source, filename, 'exec'), namespace)
    return namespace, output.getvalue().rstrip('\n')


def report_with_inputs(quantity, returned, price):
    tree = ast.parse(REPORT.read_text(encoding='utf-8'))
    overrides = {'ordered_quantity': quantity, 'returned_quantity': returned, 'unit_price_toman': price}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in overrides:
                node.value = ast.Constant(value=overrides[name])
    ast.fix_missing_locations(tree)
    return execute(tree, str(REPORT))


class ChapterTests(unittest.TestCase):
    def test_01_all_code_blocks_are_accounted_for(self):
        self.assertEqual(len(NORMAL), 28)
        self.assertEqual(len(ERRORS), 6)
        self.assertEqual(TEXT.count('```python\n'), 34)
        self.assertEqual(len(BY_ID), 28)
        self.assertEqual([cid for cid, _, _ in NORMAL[:24]], [f'C{i:02d}' for i in range(1, 25)])

    def test_02_all_printed_outputs_match(self):
        for cid, source, expected in NORMAL:
            with self.subTest(example=cid):
                _, actual = execute(source, cid)
                self.assertEqual(actual, expected)

    def test_03_all_expected_errors_match_by_type(self):
        for cid, error_name, source in ERRORS:
            with self.subTest(example=cid):
                error_class = getattr(builtins, error_name)
                with self.assertRaises(error_class):
                    execute(source, cid)

    def test_04_reference_order_exact_values(self):
        ns, output = execute(REPORT.read_text(encoding='utf-8'), str(REPORT))
        self.assertEqual(output, BY_ID['C23'][1])
        self.assertEqual(ns['initial_amount_toman'], 720000)
        self.assertEqual(ns['refund_amount_toman'], 240000)
        self.assertEqual(ns['remaining_quantity'], 2)
        self.assertEqual(ns['amount_after_returns_toman'], 480000)
        self.assertTrue(math.isclose(ns['refund_amount_ratio'], 1 / 3))
        self.assertIs(type(ns['amount_after_returns_toman']), int)

    def test_05_changed_order(self):
        ns, _ = report_with_inputs(4, 1, 240000)
        self.assertEqual(ns['initial_amount_toman'], 960000)
        self.assertEqual(ns['refund_amount_toman'], 240000)
        self.assertEqual(ns['amount_after_returns_toman'], 720000)
        self.assertEqual(ns['refund_amount_ratio'], 0.25)

    def test_06_no_returns(self):
        ns, _ = report_with_inputs(3, 0, 240000)
        self.assertEqual(ns['remaining_quantity'], 3)
        self.assertEqual(ns['refund_amount_toman'], 0)
        self.assertEqual(ns['amount_after_returns_toman'], 720000)
        self.assertEqual(ns['refund_amount_ratio'], 0.0)

    def test_07_all_items_returned(self):
        ns, _ = report_with_inputs(3, 3, 240000)
        self.assertEqual(ns['remaining_quantity'], 0)
        self.assertEqual(ns['amount_after_returns_toman'], 0)
        self.assertEqual(ns['refund_amount_ratio'], 1.0)

    def test_08_zero_denominator_not_silently_coerced(self):
        with self.assertRaises(ZeroDivisionError):
            report_with_inputs(0, 0, 240000)

    def test_09_notebook_structure_and_sequential_code(self):
        notebook_path = ROOT / 'notebooks/03-values-variables-calculation.ipynb'
        notebook = json.loads(notebook_path.read_text(encoding='utf-8'))
        self.assertEqual(notebook['nbformat'], 4)
        code_cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
        self.assertEqual(len(code_cells), 24)
        namespace = {'__name__': '__main__'}
        for number, cell in enumerate(code_cells, 1):
            with self.subTest(notebook_cell=number):
                self.assertIsNone(cell['execution_count'])
                self.assertEqual(cell['outputs'], [])
                source = ''.join(cell['source'])
                self.assertEqual(source, BY_ID[f'C{number:02d}'][0])
                output = io.StringIO()
                with redirect_stdout(output):
                    exec(compile(source, f'<notebook-C{number:02d}>', 'exec'), namespace)
                self.assertEqual(output.getvalue().rstrip('\n'), BY_ID[f'C{number:02d}'][1])
        # This verifies code semantics, not the real Jupyter kernel protocol.

    def test_10_interactive_input_with_controlled_response(self):
        output = io.StringIO()
        with patch('builtins.input', return_value='3') as mocked_input, redirect_stdout(output):
            ns = runpy.run_path(str(ROOT / 'examples/03-input-demo.py'))
        mocked_input.assert_called_once_with('تعداد کالا: ')
        self.assertEqual(output.getvalue(), '720000\n')
        self.assertIs(type(ns['quantity']), int)
        with patch('builtins.input', return_value='3.0'), redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):
                runpy.run_path(str(ROOT / 'examples/03-input-demo.py'))

    def test_11_all_scripts_run_in_separate_processes(self):
        scripts = (
            ('examples/03-basics.py', '\n'.join(expected for cid, _, expected in NORMAL if cid.startswith('C'))),
            ('examples/03-order-report.py', BY_ID['C23'][1]),
            ('solutions/03-exercise-solutions.py', '\n'.join(expected for cid, _, expected in NORMAL if cid.startswith('A'))),
        )
        for relative_path, expected in scripts:
            with self.subTest(script=relative_path):
                result = subprocess.run([sys.executable, str(ROOT / relative_path)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.rstrip('\n'), expected)
        result = subprocess.run([sys.executable, str(ROOT / 'examples/03-input-demo.py')], cwd=ROOT, input='3\n', capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'تعداد کالا: 720000\n')

    def test_12_text_assets_and_links(self):
        for path in ROOT.rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix in ('.pyc', '.zip'):
                continue
            content = path.read_text(encoding='utf-8')
            self.assertNotIn('\ufffd', content, str(path))
            if path.suffix == '.md':
                for target in re.findall(r'\]\(([^)]+)\)', content):
                    if not target.startswith(('https://', 'http://', '#')):
                        self.assertTrue((path.parent / target).is_file(), (path, target))
            if path.suffix in ('.txt', '.md'):
                columns = None
                for line in content.splitlines():
                    if line.startswith('|'):
                        columns = columns or line.count('|')
                        self.assertEqual(line.count('|'), columns, (path.name, line))
                    else:
                        columns = None
        self.assertEqual(TEXT.count('[محل درج تصویر '), 3)
        self.assertEqual(TEXT.count('[پایان محل تصویر]'), 3)

    def test_13_exercise_order_independent_expectations(self):
        ns, _ = execute(BY_ID['A10'][0], 'A10')
        self.assertEqual(ns['initial_amount_toman'], 900000)
        self.assertEqual(ns['refund_amount_toman'], 360000)
        self.assertEqual(ns['amount_after_returns_toman'], 540000)
        self.assertEqual(ns['remaining_quantity'], 3)
        self.assertEqual(ns['refund_amount_ratio'], 0.4)

    def test_14_file_artifacts_match_chapter_sources(self):
        basics = (ROOT / 'examples/03-basics.py').read_text(encoding='utf-8')
        answers = (ROOT / 'solutions/03-exercise-solutions.py').read_text(encoding='utf-8')
        for cid, source, _ in NORMAL:
            self.assertIn(source, basics if cid.startswith('C') else answers)
        self.assertIn(BY_ID['C23'][0], REPORT.read_text(encoding='utf-8'))
        lab = (ROOT / 'examples/ERROR-LAB.md').read_text(encoding='utf-8')
        for cid, error_name, source in ERRORS:
            self.assertIn(source, lab)
            self.assertIn(error_name, lab)


if __name__ == '__main__':
    unittest.main(verbosity=2)
