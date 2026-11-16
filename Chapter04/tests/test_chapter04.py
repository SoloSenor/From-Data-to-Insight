"""Regression and editorial checks for chapter 04; standard library only."""
import ast
import builtins
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / 'chapter-04-full-fa.txt').read_text(encoding='utf-8')


def parse_blocks():
    blocks = {}
    for match in re.finditer(r'```python\n(.*?)\n```', TEXT, re.S):
        heading = TEXT[:match.start()].rstrip().splitlines()[-1]
        block_id = re.search(r'\b([CAE]\d{2})\b', heading).group(1)
        output = re.match(r'\n\s*[^\n]*:\n```text\n(.*?)\n```',
                          TEXT[match.end():], re.S)
        if block_id in blocks:
            raise ValueError('Duplicate block ID: ' + block_id)
        blocks[block_id] = {
            'code': match.group(1) + '\n',
            'output': None if block_id.startswith('E') else output.group(1) + '\n',
        }
    return blocks


BLOCKS = parse_blocks()


def run(code):
    output = io.StringIO()
    namespace = {'__name__': '__chapter_test__'}
    with redirect_stdout(output):
        exec(compile(code, '<chapter04>', 'exec'), namespace)
    return output.getvalue(), namespace


def script_blocks(path):
    source = path.read_text(encoding='ascii')
    return dict(re.findall(r'# BEGIN ([CA]\d{2})\n(.*?)# END \1\n', source, re.S))


class Chapter04Tests(unittest.TestCase):
    def test_01_inventory_and_fresh_execution(self):
        expected = ({f'C{i:02}' for i in range(1, 25)} |
                    {f'E{i:02}' for i in range(1, 7)} |
                    {'A01', 'A02', 'A03', 'A04', 'A06', 'A08', 'A09', 'A12'})
        self.assertEqual(set(BLOCKS), expected)
        for name, block in BLOCKS.items():
            if not name.startswith('E'):
                with self.subTest(block=name):
                    self.assertEqual(run(block['code'])[0], block['output'])

    def test_02_intentional_exceptions(self):
        errors = {'E01': IndexError, 'E02': ValueError, 'E03': KeyError,
                  'E04': TypeError, 'E05': TypeError, 'E06': TypeError}
        payload = json.loads((ROOT / 'examples/04-intentional-errors.json').read_text())
        self.assertEqual({item['id'] for item in payload}, set(errors))
        for item in payload:
            with self.subTest(block=item['id']):
                self.assertEqual(item['code'], BLOCKS[item['id']]['code'])
                self.assertEqual(getattr(builtins, item['exception']), errors[item['id']])
                with self.assertRaises(errors[item['id']]):
                    run(item['code'])

    def test_03_ascii_code_and_output(self):
        for name, block in BLOCKS.items():
            with self.subTest(block=name):
                self.assertTrue(block['code'].isascii())
                if block['output'] is not None:
                    self.assertTrue(block['output'].isascii())
        for path in ROOT.rglob('*.py'):
            self.assertTrue(path.read_text(encoding='utf-8').isascii(), str(path))
        for output in re.findall(r'```text\n(.*?)\n```', TEXT, re.S):
            self.assertTrue(output.isascii())

    def test_04_beginner_scope(self):
        prohibited = (ast.For, ast.While, ast.If, ast.IfExp, ast.FunctionDef,
                      ast.AsyncFunctionDef, ast.Lambda, ast.ListComp,
                      ast.DictComp, ast.SetComp, ast.GeneratorExp, ast.ClassDef,
                      ast.Try, ast.Import, ast.ImportFrom)
        for name, block in BLOCKS.items():
            with self.subTest(block=name):
                self.assertFalse(any(isinstance(node, prohibited)
                                     for node in ast.walk(ast.parse(block['code']))))

    def test_05_scripts_match_chapter(self):
        for prefix, relative in [('C', 'examples/04-examples.py'),
                                 ('A', 'solutions/04-solutions.py')]:
            expected = {name: item['code'] for name, item in BLOCKS.items()
                        if name.startswith(prefix)}
            self.assertEqual(script_blocks(ROOT / relative), expected)
        self.assertEqual((ROOT / 'examples/04-orders-workshop.py').read_text(),
                         BLOCKS['C24']['code'])

    def test_06_scripts_in_subprocesses(self):
        for relative, prefix in [('examples/04-examples.py', 'C'),
                                 ('solutions/04-solutions.py', 'A'),
                                 ('examples/04-orders-workshop.py', 'C24')]:
            with self.subTest(script=relative):
                proc = subprocess.run([sys.executable, str(ROOT / relative)],
                                      capture_output=True, text=True, timeout=30,
                                      cwd=ROOT)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                expected = ''.join(b['output'] for name, b in BLOCKS.items()
                                   if name.startswith(prefix))
                self.assertEqual(proc.stdout, expected)
                self.assertEqual(proc.stderr, '')

    def test_07_workshop_independent_oracle(self):
        _, ns = run(BLOCKS['C24']['code'])
        self.assertEqual(ns['orders'], [
            {'order_id': 'O-0401', 'quantity': 3, 'unit_price_toman': 240000,
             'returned_quantity': 1},
            {'order_id': 'O-0402', 'quantity': 2, 'unit_price_toman': 80000,
             'returned_quantity': 0},
            {'order_id': 'O-0403', 'quantity': 1, 'unit_price_toman': 300000,
             'returned_quantity': 1},
        ])
        self.assertEqual(ns['gross_amounts_toman'], [720000, 160000, 300000])
        self.assertEqual(ns['refund_amounts_toman'], [240000, 0, 300000])
        self.assertEqual(ns['gross_total_toman'], 1180000)
        self.assertEqual(ns['refund_total_toman'], 540000)
        self.assertEqual(ns['after_returns_toman'], 640000)
        self.assertEqual(sum(o['quantity'] for o in ns['orders']), 6)
        self.assertEqual(sum(o['returned_quantity'] for o in ns['orders']), 2)
        self.assertIs(ns['first'], ns['orders'][0])

    def test_08_workshop_changed_inputs(self):
        changed = BLOCKS['C24']['code'].replace('240_000', '100_000', 1)
        _, ns = run(changed)
        self.assertEqual(ns['gross_total_toman'], 760000)
        self.assertEqual(ns['refund_total_toman'], 400000)
        self.assertEqual(ns['after_returns_toman'], 360000)

    def test_09_workshop_zero_and_full_returns(self):
        code = BLOCKS['C24']['code']
        zero = code.replace('"returned_quantity": 1', '"returned_quantity": 0')
        _, ns = run(zero)
        self.assertEqual(ns['refund_total_toman'], 0)
        self.assertEqual(ns['after_returns_toman'], 1180000)
        full = code.replace('"returned_quantity": 1', '"returned_quantity": 3', 1)
        full = full.replace('"returned_quantity": 0', '"returned_quantity": 2', 1)
        _, ns = run(full)
        self.assertEqual(ns['refund_total_toman'], 1180000)
        self.assertEqual(ns['after_returns_toman'], 0)

    def test_10_workshop_zero_prices(self):
        code = BLOCKS['C24']['code']
        for price in ('240_000', '80_000', '300_000'):
            code = code.replace(price, '0')
        _, ns = run(code)
        self.assertEqual(ns['gross_total_toman'], 0)
        self.assertEqual(ns['refund_total_toman'], 0)
        self.assertEqual(ns['after_returns_toman'], 0)

    def test_11_index_slice_and_empty_boundaries(self):
        self.assertEqual([3, 1, 4, 2][1:3], [1, 4])
        self.assertEqual([3, 1, 4, 2][99:], [])
        self.assertEqual([][:2], [])
        with self.assertRaises(IndexError):
            [][-1]
        with self.assertRaises(IndexError):
            values = [1]
            values[1] = 2
        with self.assertRaises(ValueError):
            [1, 2][::0]
        self.assertEqual(sum([]), 0)

    def test_12_list_mutator_contracts(self):
        values = []
        self.assertIsNone(values.append(1))
        self.assertIsNone(values.extend([2, 3]))
        self.assertIsNone(values.insert(0, 0))
        self.assertIsNone(values.remove(2))
        self.assertEqual(values.pop(), 3)
        self.assertEqual(values, [0, 1])
        self.assertIsNone(values.sort())
        with self.assertRaises(ValueError):
            values.remove(999)
        with self.assertRaises(IndexError):
            [].pop()
        ids = []
        ids.extend('AB')
        self.assertEqual(ids, ['A', 'B'])

    def test_13_dict_missing_none_zero_and_order(self):
        data = {'none': None, 'zero': 0}
        self.assertIsNone(data.get('none', 500))
        self.assertEqual(data.get('zero', 500), 0)
        self.assertEqual(data.get('absent', 500), 500)
        self.assertNotIn('absent', data)
        self.assertIsNone(data.get('absent'))
        self.assertEqual(list(data), ['none', 'zero'])
        view = data.keys()
        snapshot = list(view)
        data['later'] = 1
        self.assertIn('later', view)
        self.assertNotIn('later', snapshot)
        repeated = {'same': 1, 'same': 2}
        self.assertEqual(repeated, {'same': 2})
        with self.assertRaises(KeyError):
            {'quantity': 1}[0]

    def test_14_alias_shallow_copy_and_tuple(self):
        _, ns = run(BLOCKS['C10']['code'])
        self.assertIs(ns['original'], ns['alias'])
        _, ns = run(BLOCKS['C11']['code'])
        self.assertIsNot(ns['original'], ns['working'])
        original = [{'quantity': 3}]
        working = original.copy()
        self.assertIsNot(original, working)
        self.assertIs(original[0], working[0])
        working[0]['quantity'] = 9
        self.assertEqual(original[0]['quantity'], 9)
        _, ns = run(BLOCKS['C18']['code'])
        self.assertEqual(ns['record'], ('O-0401', [3, 1, 4]))
        with self.assertRaises(TypeError):
            hash(('O-0401', []))
        with self.assertRaises(ValueError):
            first, second = (1,)

    def test_15_sets_frequency_and_hashability(self):
        self.assertEqual(len(set(['A', 'A', 'A'])), 1)
        self.assertIsInstance({}, dict)
        self.assertIsInstance(set(), set)
        values = {'A'}
        values.add('A')
        self.assertEqual(len(values), 1)
        self.assertIsNone(values.discard('missing'))
        with self.assertRaises(KeyError):
            values.remove('missing')
        with self.assertRaises(TypeError):
            values[0]
        with self.assertRaises(TypeError):
            values.add({})

    def test_16_logical_error_and_stale_value_witnesses(self):
        _, ns = run(BLOCKS['C22']['code'])
        self.assertEqual(ns['order_ids'][0], 'O-0401')
        self.assertNotEqual(ns['amounts_toman'][0], 720000)
        self.assertEqual(len(ns['order_ids']), len(ns['amounts_toman']))
        _, ns = run(BLOCKS['C23']['code'])
        self.assertEqual(ns['order']['gross_toman'], 720000)
        self.assertEqual(ns['order']['quantity'] * ns['order']['unit_price_toman'], 480000)
        self.assertEqual(sorted(['20', '100']), ['100', '20'])
        with self.assertRaises(TypeError):
            sorted([{'quantity': 3}, {'quantity': 1}])

    def test_17_answer_oracles(self):
        expected = {
            'A01': '1\n[2, 8]\n[]\n',
            'A02': '[1, 2, [3, 4]] 3\n[1, 2, 3, 4] 4\n',
            'A03': "['new']\npaid\n",
            'A04': '[90000, 50000, 10000]\n[90000, 10000, 50000]\n',
            'A06': 'O-0411\n300000\n',
            'A08': '1\n10\n',
            'A09': "['O-0401', 'O-0403']\n['O-0404']\n",
            'A12': '100000\n100000\n0\n',
        }
        for name, oracle in expected.items():
            with self.subTest(block=name):
                self.assertEqual(run(BLOCKS[name]['code'])[0], oracle)

    def test_18_notebook_clean_matching_and_sequential(self):
        nb = json.loads((ROOT / 'notebooks/04-data-structures.ipynb').read_text())
        self.assertEqual(nb['nbformat'], 4)
        self.assertEqual(nb['metadata']['kernelspec']['name'], 'python3')
        cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
        self.assertEqual(len(cells), 24)
        shared = {'__name__': '__chapter_notebook__'}
        for index, cell in enumerate(cells, 1):
            name = f'C{index:02}'
            self.assertEqual(cell['metadata']['chapter_block_id'], name)
            self.assertEqual(cell['outputs'], [])
            self.assertIsNone(cell['execution_count'])
            code = ''.join(cell['source'])
            self.assertTrue(code.isascii())
            self.assertEqual(code, BLOCKS[name]['code'])
            output = io.StringIO()
            with redirect_stdout(output):
                exec(compile(code, '<notebook>', 'exec'), shared)
            self.assertEqual(output.getvalue(), BLOCKS[name]['output'])

    def test_19_local_links_utf8_and_content_inventory(self):
        for path in ROOT.rglob('*'):
            if path.is_file() and path.suffix in {'.md', '.txt', '.py', '.json', '.ipynb'}:
                content = path.read_text(encoding='utf-8')
                self.assertNotIn('\ufffd', content)
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', readme):
            if not target.startswith(('http:', 'https:')):
                self.assertTrue((ROOT / target).is_file(), target)
        self.assertEqual(len(re.findall('^\u062c\u0627\u06cc\u06af\u0627\u0647 \u062a\u0635\u0648\u06cc\u0631 [\u06f1\u06f2\u06f3]', TEXT, re.M)), 3)
        for i in range(1, 13):
            digits = str(i).translate(str.maketrans('0123456789', '\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9'))
            self.assertIn('\u062a\u0645\u0631\u06cc\u0646 ' + digits + ' ', TEXT)
        self.assertIn('1,180,000', TEXT)
        self.assertIn('640,000', TEXT)

    def test_20_scope_limit_is_observable(self):
        code = BLOCKS['C24']['code']
        short = code.replace('third = orders[2]', 'orders.pop()\nthird = orders[2]')
        with self.assertRaises(IndexError):
            run(short)
        extra = code.replace('first = orders[0]',
                             'orders.append({"order_id": "O-0404", "quantity": 1, '
                             '"unit_price_toman": 1, "returned_quantity": 0})\nfirst = orders[0]')
        output, ns = run(extra)
        self.assertIn('Order records: 4\n', output)
        self.assertEqual(ns['gross_total_toman'], 1180000)
        self.assertEqual(len(ns['gross_amounts_toman']), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
