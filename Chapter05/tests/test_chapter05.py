import ast
import contextlib
import copy
import io
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / 'chapter-05-full-fa.txt').read_text(encoding='utf-8')
PATTERN = r'^### ([CAE]\d{2}) \u2014 ([^\n]+)\n\n```python\n(.*?)```(?:\n\n\u062e\u0631\u0648\u062c\u06cc \u0645\u0648\u0631\u062f\u0627\u0646\u062a\u0638\u0627\u0631:\n\n```text\n(.*?)```)?'
BLOCKS = [dict(id=i, title=t, code=c, output=o or None) for i, t, c, o in re.findall(PATTERN, TEXT, re.M | re.S)]
BY_ID = {b['id']: b for b in BLOCKS}
GOOD = [b for b in BLOCKS if not b['id'].startswith('E')]


def execute(code, namespace=None):
    namespace = {} if namespace is None else namespace
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exec(compile(code, '<chapter-example>', 'exec'), namespace)
    return stream.getvalue(), namespace


def workshop_functions():
    code = BY_ID['C21']['code'].split('\norders = [', 1)[0]
    return execute(code)[1]


def discount_functions():
    code = BY_ID['C19']['code'].split('\nquote = ', 1)[0]
    return execute(code)[1]


def record(q=3, p=240_000, r=1, identifier='O-T'):
    return dict(order_id=identifier, quantity=q, unit_price_toman=p, returned_quantity=r)


def sample():
    return [record(), record(2, 80_000, 0, 'O-B'), record(1, 300_000, 1, 'O-C')]


class Chapter05Tests(unittest.TestCase):
    def test_01_inventory(self):
        self.assertEqual(len(BLOCKS), 39)
        self.assertEqual(len(BY_ID), len(BLOCKS))
        self.assertEqual([b['id'] for b in BLOCKS if b['id'].startswith('C')], [f'C{i:02}' for i in range(1, 26)])
        self.assertEqual([b['id'] for b in BLOCKS if b['id'].startswith('A')], ['A01', 'A03', 'A04', 'A06', 'A07', 'A08', 'A10', 'A12'])
        self.assertEqual(len(re.findall(r'^### \u062a\u0645\u0631\u06cc\u0646 \d+ \u2014', TEXT, re.M)), 12)
        self.assertEqual(len(re.findall(r'^\[\u062c\u0627\u06cc\u06af\u0627\u0647 \u062a\u0635\u0648\u06cc\u0631 [\u06f1\u06f2\u06f3]:', TEXT, re.M)), 3)

    def test_02_outputs_in_fresh_namespaces(self):
        for b in GOOD:
            with self.subTest(block=b['id']):
                self.assertIsNotNone(b['output'])
                actual, _ = execute(b['code'])
                self.assertEqual(actual, b['output'])

    def test_03_exact_intentional_exception_types(self):
        items = json.loads((ROOT / 'examples/05-intentional-errors.json').read_text())
        self.assertEqual(len(items), 6)
        for item in items:
            with self.subTest(block=item['id']):
                self.assertEqual(BY_ID[item['id']]['code'], item['code'])
                try:
                    execute(item['code'])
                except Exception as error:
                    self.assertEqual(type(error).__name__, item['exception'])
                else:
                    self.fail('Expected exception was not raised')

    def test_04_ascii_code_outputs_and_sources(self):
        for b in BLOCKS:
            self.assertTrue(b['code'].isascii(), b['id'])
            if b['output'] is not None:
                self.assertTrue(b['output'].isascii(), b['id'])
        for path in ROOT.rglob('*.py'):
            self.assertTrue(path.read_text().isascii(), str(path))
            ast.parse(path.read_text())
        for code in re.findall(r'```python\n(.*?)```', TEXT, re.S):
            self.assertTrue(code.isascii())

    def test_05_readable_script_code_matches_text(self):
        for prefix, rel in [('C', 'examples/05-examples.py'), ('A', 'solutions/05-solutions.py')]:
            expected = ''.join('# ' + b['id'] + '\n' + b['code'] + '\n' for b in GOOD if b['id'].startswith(prefix))
            self.assertEqual((ROOT / rel).read_text(), expected)
        self.assertEqual((ROOT / 'examples/05-workshop.py').read_text(), BY_ID['C21']['code'])

    def test_06_scripts_run_as_separate_processes(self):
        for prefix, rel in [('C', 'examples/05-examples.py'), ('A', 'solutions/05-solutions.py')]:
            run = subprocess.run([sys.executable, str(ROOT / rel)], text=True, capture_output=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout, ''.join(b['output'] for b in GOOD if b['id'].startswith(prefix)))
        run = subprocess.run([sys.executable, str(ROOT / 'examples/05-workshop.py')], text=True, capture_output=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, BY_ID['C21']['output'])
        run = subprocess.run([sys.executable, str(ROOT / 'examples/05-discount.py')], text=True, capture_output=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, 'gross_toman 720000\ndiscount_toman 50000\npayable_toman 670000\n')

    def test_07_workshop_independent_golden_values(self):
        funcs = workshop_functions()
        results = [funcs['analyze_order'](o) for o in sample()]
        self.assertEqual([x['gross_toman'] for x in results], [720_000, 160_000, 300_000])
        self.assertEqual([x['refund_toman'] for x in results], [240_000, 0, 300_000])
        self.assertEqual([x['after_returns_toman'] for x in results], [480_000, 160_000, 0])
        self.assertEqual([x['return_status'] for x in results], ['partial_return', 'no_return', 'full_return'])
        self.assertEqual(funcs['summarize_orders'](sample()), {
            'order_count': 3, 'total_quantity': 6, 'total_returned_quantity': 2,
            'orders_with_return': 2, 'gross_toman': 1_180_000,
            'refund_toman': 540_000, 'after_returns_toman': 640_000,
        })

    def test_08_fourth_record_and_changed_price(self):
        orders = sample() + [record(2, 50_000, 0, 'O-D')]
        summary = workshop_functions()['summarize_orders']
        self.assertEqual(summary(orders), dict(order_count=4, total_quantity=8, total_returned_quantity=2,
                                             orders_with_return=2, gross_toman=1_280_000,
                                             refund_toman=540_000, after_returns_toman=740_000))
        orders[-1]['unit_price_toman'] = 70_000
        result = summary(orders)
        self.assertEqual(result['gross_toman'], 1_320_000)
        self.assertEqual(result['refund_toman'], 540_000)
        self.assertEqual(result['after_returns_toman'], 780_000)

    def test_09_empty_single_and_fresh_reports(self):
        summary = workshop_functions()['summarize_orders']
        empty = summary([])
        self.assertEqual(list(empty.values()), [0] * 7)
        one = summary([record(2, 7, 1)])
        self.assertEqual(one, dict(order_count=1, total_quantity=2, total_returned_quantity=1,
                                   orders_with_return=1, gross_toman=14, refund_toman=7, after_returns_toman=7))
        empty['order_count'] = 99
        self.assertEqual(summary([])['order_count'], 0)
        self.assertEqual(summary(sample()), summary(sample()))

    def test_10_zero_and_full_returns(self):
        funcs = workshop_functions()
        for q in range(1, 7):
            for p in [0, 1, 7, 240_000]:
                with self.subTest(q=q, p=p):
                    no_return = funcs['analyze_order'](record(q, p, 0))
                    full_return = funcs['analyze_order'](record(q, p, q))
                    self.assertEqual(no_return['refund_toman'], 0)
                    self.assertEqual(no_return['after_returns_toman'], q * p)
                    self.assertEqual(no_return['return_status'], 'no_return')
                    self.assertEqual(full_return['after_returns_toman'], 0)
                    self.assertEqual(full_return['refund_toman'], q * p)
                    self.assertEqual(full_return['return_status'], 'full_return')

    def test_11_small_valid_domain_independent_formula(self):
        analyze = workshop_functions()['analyze_order']
        cases = 0
        for q in range(1, 7):
            for r in range(q + 1):
                for p in [0, 1, 7, 240_000]:
                    result = analyze(record(q, p, r))
                    self.assertEqual(result['after_returns_toman'], (q - r) * p)
                    self.assertEqual(result['gross_toman'], result['refund_toman'] + result['after_returns_toman'])
                    self.assertGreaterEqual(result['after_returns_toman'], 0)
                    cases += 1
        self.assertEqual(cases, 108)

    def test_12_deterministic_larger_sample_and_permutation(self):
        rng = random.Random(5005)
        orders = []
        expected_gross = expected_refund = expected_kept = expected_units = expected_returned = expected_with_return = 0
        for i in range(100):
            q = rng.randint(1, 8)
            p = rng.randint(0, 100_000)
            r = rng.randint(0, q)
            orders.append(record(q, p, r, f'O-{i}'))
            # Unit-wise addition is an independent, deliberately simple oracle.
            expected_gross += sum([p] * q)
            expected_refund += sum([p] * r)
            expected_kept += sum([p] * (q - r))
            expected_units += q
            expected_returned += r
            expected_with_return += int(r > 0)
        summary = workshop_functions()['summarize_orders']
        expected = dict(order_count=100, total_quantity=expected_units, total_returned_quantity=expected_returned,
                        orders_with_return=expected_with_return, gross_toman=expected_gross,
                        refund_toman=expected_refund, after_returns_toman=expected_kept)
        self.assertEqual(summary(orders), expected)
        self.assertEqual(summary(list(reversed(orders))), expected)

    def test_13_input_unchanged_and_new_output(self):
        funcs = workshop_functions()
        orders = sample()
        before = copy.deepcopy(orders)
        result = funcs['analyze_order'](orders[0])
        funcs['summarize_orders'](orders)
        self.assertEqual(orders, before)
        self.assertIsNot(result, orders[0])
        result['quantity'] = 999
        self.assertEqual(orders, before)

    def test_14_discount_boundaries_and_quote(self):
        funcs = discount_functions()
        for amount, expected in [(0, 0), (1, 0), (499_999, 0), (500_000, 50_000), (500_001, 50_000),
                                  (999_999, 50_000), (1_000_000, 100_000), (1_000_001, 100_000)]:
            self.assertEqual(funcs['discount_for'](amount), expected)
        self.assertEqual(funcs['quote_order'](3, 240_000), dict(gross_toman=720_000, discount_toman=50_000, payable_toman=670_000))
        self.assertEqual(funcs['quote_order'](2, 0)['payable_toman'], 0)

    def test_15_three_ratios_and_zero_price_status(self):
        report = workshop_functions()['summarize_orders'](sample())
        self.assertAlmostEqual(report['orders_with_return'] / report['order_count'], 2 / 3)
        self.assertAlmostEqual(report['total_returned_quantity'] / report['total_quantity'], 1 / 3)
        self.assertAlmostEqual(report['refund_toman'] / report['gross_toman'], 27 / 59)
        result = workshop_functions()['analyze_order'](record(2, 0, 1))
        self.assertEqual(result['return_status'], 'partial_return')
        self.assertEqual(result['after_returns_toman'], 0)

    def test_16_solution_functions_with_new_inputs(self):
        band = execute(BY_ID['A01']['code'])[1]['amount_band']
        self.assertEqual(band(0), 'small')
        self.assertEqual(band(999_999), 'medium')
        kept = execute(BY_ID['A06']['code'])[1]['kept_amount']
        self.assertEqual(kept(5, 7, 2), 21)
        returned = execute(BY_ID['A07']['code'])[1]['returned_ids']
        orders = [record(1, 1, 1, 'A'), record(2, 1, 0, 'B'), record(2, 1, 1, 'C')]
        before = copy.deepcopy(orders)
        self.assertEqual(returned(orders), ['A', 'C'])
        self.assertEqual(orders, before)
        share = execute(BY_ID['A08']['code'])[1]['safe_share']
        self.assertEqual(share(0, 4), 0)
        self.assertIsNone(share(0, 0))
        count = execute(BY_ID['A12']['code'])[1]['count_above']
        self.assertEqual(count([12, 12], 12), 0)
        self.assertEqual(count([13, 14], 12), 2)

    def test_17_truth_short_circuit_and_control_flow(self):
        self.assertEqual(execute(BY_ID['C02']['code'])[0], 'False\nFalse\nFalse\nTrue\nTrue\nTrue\n')
        self.assertFalse(execute(BY_ID['C06']['code'])[1]['has_high_return'])
        with self.assertRaises(ZeroDivisionError):
            execute('q = 0\nx = (0 / q > 0.5) and (q > 0)\n')
        self.assertEqual(execute(BY_ID['C12']['code'])[1]['missing_count'], 1)
        self.assertEqual(execute(BY_ID['C13']['code'])[1]['first_positive'], 2)
        self.assertEqual(execute(BY_ID['C14']['code'])[1]['attempt'], 4)

    def test_18_logical_bug_witnesses(self):
        bad_reset = 'total = 0\nfor value in [3, 2, 1]:\n    total = 0\n    total += value\n'
        self.assertEqual(execute(bad_reset)[1]['total'], 1)
        core = BY_ID['C21']['code'].split('\norders = [', 1)[0]
        broken = core.replace('    return report\n', '        return report\n')
        broken_funcs = execute(broken)[1]
        self.assertEqual(broken_funcs['summarize_orders'](sample())['order_count'], 1)
        bad_tier = 'def tier(x):\n    if x >= 500_000:\n        return "medium"\n    elif x >= 1_000_000:\n        return "large"\n'
        self.assertEqual(execute(bad_tier)[1]['tier'](1_000_000), 'medium')

    def test_19_out_of_contract_limit_is_explicit(self):
        funcs = workshop_functions()
        invalid = funcs['analyze_order'](record(1, 10, 2))
        self.assertEqual(invalid['after_returns_toman'], -10)
        self.assertEqual(invalid['return_status'], 'partial_return')
        with self.assertRaises(KeyError):
            funcs['analyze_order']({'quantity': 1})
        duplicates = [record(1, 10, 0, 'same'), record(1, 10, 0, 'same')]
        self.assertEqual(funcs['summarize_orders'](duplicates)['order_count'], 2)
        # These observed limitations are not accepted business behavior.
        self.assertIn('\u0627\u0639\u062a\u0628\u0627\u0631\u0633\u0646\u062c\u06cc \u0646\u0645\u06cc\u200c\u06a9\u0646\u062f', TEXT)
        self.assertIn('bool \u062a\u0639\u062f\u0627\u062f \u06cc\u0627 \u0642\u06cc\u0645\u062a \u0645\u062d\u0633\u0648\u0628 \u0646\u0645\u06cc\u200c\u0634\u0648\u062f', TEXT)

    def test_20_introductory_scope(self):
        forbidden = (ast.Import, ast.ImportFrom, ast.ClassDef, ast.Lambda, ast.ListComp, ast.DictComp,
                     ast.SetComp, ast.GeneratorExp, ast.Try, ast.Raise, ast.AsyncFunctionDef, ast.Global, ast.Nonlocal)
        for b in GOOD:
            tree = ast.parse(b['code'])
            self.assertFalse(any(isinstance(n, forbidden) for n in ast.walk(tree)), b['id'])

    def test_21_notebook_clean_matching_sequential(self):
        import nbformat
        nb = nbformat.read(ROOT / 'notebooks/05-control-flow-functions.ipynb', as_version=4)
        nbformat.validate(nb)
        cells = [c for c in nb.cells if c.cell_type == 'code']
        self.assertEqual(len(cells), 25)
        namespace = {}
        for cell in cells:
            expected = BY_ID[cell.metadata['example_id']]
            self.assertEqual(cell.source, expected['code'])
            self.assertTrue(cell.source.isascii())
            self.assertIsNone(cell.execution_count)
            self.assertEqual(cell.outputs, [])
            self.assertEqual(execute(cell.source, namespace)[0], expected['output'])

    def test_22_local_readme_links_and_utf8(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for destination in re.findall(r'\]\(([^)]+)\)', readme):
            if not destination.startswith(('http:', 'https:', '#')):
                self.assertTrue((ROOT / destination).is_file(), destination)
        for path in ROOT.rglob('*'):
            if path.is_file() and path.suffix in {'.txt', '.md', '.py', '.json', '.ipynb', '.in'}:
                self.assertNotIn('\ufffd', path.read_text(encoding='utf-8'), str(path))

    def test_23_asserts_really_fail(self):
        with self.assertRaises(AssertionError):
            execute('assert 1 == 2\n')
        self.assertFalse(sys.flags.optimize, 'Run tests without -O')
        self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(BY_ID['C25']['code']))), 12)

    def test_24_appendix_quote_matches_chapter(self):
        chapter_defs = BY_ID['C19']['code'].split('\nquote = ', 1)[0]
        script_defs = (ROOT / 'examples/05-discount.py').read_text().split('\nquote = ', 1)[0]
        self.assertEqual(chapter_defs, script_defs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
