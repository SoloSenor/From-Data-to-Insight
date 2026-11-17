"""Reproducible chapter 09 checks; standard library only."""
import contextlib
import copy
import csv
from datetime import date
import io
import json
from pathlib import Path, PureWindowsPath
import random
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from order_report.file_io import (
    FIELDS, INTEGER_FIELDS, read_orders_csv, read_orders_json,
    validate_orders, write_orders_csv, write_orders_json,
)
from order_report.reporting import build_report, format_report


def load_catalog(name):
    return json.loads((ROOT / 'examples' / name).read_text(encoding='utf-8'))


class Chapter09Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='chapter09-test-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.rows = read_orders_json(ROOT / 'data/orders.json')

    def write_csv_text(self, text):
        path = self.folder / 'input.csv'
        path.write_text(text, encoding='utf-8', newline='')
        return path

    def write_json_value(self, value):
        path = self.folder / 'input.json'
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def altered(self, field, value):
        rows = copy.deepcopy(self.rows)
        rows[0][field] = value
        return rows

    def run_code(self, code):
        result = subprocess.run([sys.executable, '-c', code], cwd=self.folder,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout

    def test_01_thirty_examples_independently(self):
        catalog = load_catalog('catalog.json')
        self.assertEqual(len(catalog), 30)
        for item in catalog:
            with self.subTest(example=item['id']):
                self.assertEqual(self.run_code(item['code']), item['output'])

    def test_02_full_example_script(self):
        expected = (ROOT / 'outputs/examples.txt').read_text(encoding='ascii')
        actual = self.run_code((ROOT / 'examples/09-examples.py').read_text())
        self.assertEqual(actual, expected)

    def test_03_eight_coding_answers(self):
        answers = load_catalog('answers.json')
        self.assertEqual([a['exercise'] for a in answers], list(range(5, 13)))
        for item in answers:
            with self.subTest(answer=item['id']):
                self.assertEqual(self.run_code(item['code']), item['output'])

    def test_04_intentional_error_types(self):
        errors = load_catalog('intentional-errors.json')
        self.assertEqual(len(errors), 8)
        for item in errors:
            with self.subTest(error=item['id']):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    try:
                        exec(compile(item['code'], item['id'], 'exec'), {})
                    except Exception as exc:
                        self.assertEqual(type(exc).__name__, item['exception'])
                    else:
                        self.fail('Expected an exception')
                self.assertEqual(out.getvalue(), '')

    def test_05_ascii_python_outputs_and_fences(self):
        for path in ROOT.rglob('*.py'):
            self.assertTrue(path.read_text(encoding='utf-8').isascii(), str(path))
        for name in ['catalog.json', 'answers.json', 'intentional-errors.json']:
            for item in load_catalog(name):
                self.assertTrue(item['code'].isascii())
                if 'output' in item:
                    self.assertTrue(item['output'].isascii())
        text = (ROOT / 'chapter-09-full-fa.md').read_text(encoding='utf-8')
        fences = re.findall(r'```(\w*)\n(.*?)\n```', text, re.S)
        self.assertTrue(fences)
        for lang, code in fences:
            self.assertTrue(code.isascii(), lang)
            if lang == 'python':
                compile(code, '<book-fence>', 'exec')
        for path in (ROOT / 'outputs').glob('*.txt'):
            self.assertTrue(path.read_text().isascii())

    def test_06_narrative_examples_match_catalog(self):
        text = (ROOT / 'chapter-09-full-fa.md').read_text(encoding='utf-8')
        for item in load_catalog('catalog.json'):
            self.assertIn('```python\n' + item['code'].rstrip() + '\n```', text)
            self.assertIn('```text\n' + item['output'].rstrip() + '\n```', text)
        for name in ['answers.json', 'intentional-errors.json']:
            for item in load_catalog(name):
                self.assertIn('```python\n' + item['code'].rstrip() + '\n```', text)
        self.assertEqual(text, (ROOT / 'chapter-09-full-fa.txt').read_text())

    def test_07_reference_inputs_equal(self):
        self.assertEqual(read_orders_csv(ROOT / 'data/orders.csv'), self.rows)
        self.assertEqual(len(self.rows), 12)
        self.assertIsNone(validate_orders(self.rows))

    def test_08_reference_amounts_independent(self):
        gross = sum(r['quantity'] * r['unit_price_toman'] for r in self.rows)
        refund = sum(r['returned_quantity'] * r['unit_price_toman'] for r in self.rows)
        self.assertEqual((gross, refund, gross-refund), (5020000, 1430000, 3590000))
        text = format_report(build_report(self.rows))
        self.assertIn('gross_toman 5020000', text)
        self.assertIn('retained_toman 3590000', text)

    def test_09_project_two_entry_points_from_other_directory(self):
        expected = (ROOT / 'outputs/report.txt').read_text()
        cmds = [[sys.executable, str(ROOT / 'run_analysis.py')],
                [sys.executable, '-m', 'order_report']]
        for command in cmds:
            with self.subTest(command=command):
                import os
                env = dict(os.environ, PYTHONPATH=str(ROOT))
                result = subprocess.run(command, cwd=self.folder, env=env,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, '')

    def test_10_quiet_import(self):
        code = ('import sys; sys.path.insert(0, ' + repr(str(ROOT)) + '); '
                'import order_report; import order_report.cli; '
                'import order_report.file_io; import run_analysis')
        self.assertEqual(self.run_code(code), '')

    def test_11_csv_round_trip(self):
        path = self.folder / 'out.csv'
        write_orders_csv(self.rows, path)
        self.assertEqual(read_orders_csv(path), self.rows)
        self.assertFalse(path.read_bytes().startswith(b'\xef\xbb\xbf'))
        self.assertNotIn(b'\r\n', path.read_bytes())

    def test_12_json_round_trip(self):
        path = self.folder / 'out.json'
        write_orders_json(self.rows, path)
        self.assertEqual(read_orders_json(path), self.rows)
        self.assertTrue(path.read_bytes().isascii())
        self.assertTrue(path.read_bytes().endswith(b'\n'))

    def test_13_create_only_preserves_existing(self):
        for writer in [write_orders_csv, write_orders_json]:
            with self.subTest(writer=writer.__name__):
                path = self.folder / writer.__name__
                path.write_bytes(b'APPROVED')
                with self.assertRaises(FileExistsError):
                    writer(self.rows, path)
                self.assertEqual(path.read_bytes(), b'APPROVED')

    def test_14_explicit_overwrite(self):
        for writer, reader in [(write_orders_csv, read_orders_csv),
                               (write_orders_json, read_orders_json)]:
            path = self.folder / writer.__name__
            path.write_bytes(b'old')
            writer(self.rows, path, overwrite=True)
            self.assertEqual(reader(path), self.rows)

    def test_15_invalid_data_before_truncation(self):
        for writer in [write_orders_csv, write_orders_json]:
            path = self.folder / writer.__name__
            path.write_bytes(b'APPROVED')
            with self.assertRaises(ValueError):
                writer(self.altered('quantity', 0), path, overwrite=True)
            self.assertEqual(path.read_bytes(), b'APPROVED')

    def test_16_no_parent_creation(self):
        for writer in [write_orders_csv, write_orders_json]:
            path = self.folder / writer.__name__ / 'out'
            with self.assertRaises(FileNotFoundError):
                writer(self.rows, path)
            self.assertFalse(path.parent.exists())

    def test_17_empty_sets(self):
        validate_orders([])
        for writer, reader in [(write_orders_csv, read_orders_csv),
                               (write_orders_json, read_orders_json)]:
            path = self.folder / writer.__name__
            writer([], path)
            self.assertEqual(reader(path), [])

    def test_18_root_must_be_list(self):
        for value in [{}, None, 'text', 2, tuple(self.rows)]:
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(ValueError):
                    validate_orders(value)

    def test_19_record_must_be_dict_and_exact_schema(self):
        short = dict(self.rows[0]); short.pop('category')
        extra = dict(self.rows[0], unexpected=1)
        for value in [None, [], 3, short, extra]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_orders([value])

    def test_20_text_fields_nonempty_no_outer_whitespace(self):
        for field in ['order_id', 'order_date', 'category']:
            for value in ['', ' ', None, 12, ' A', 'A ']:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        validate_orders(self.altered(field, value))

    def test_21_canonical_dates_and_leap_days(self):
        for value in ['2025-02-29', '2025-13-01', '2025-1-01',
                      '20250101', '2025-01-01T00:00:00', '2025-W01-1']:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_orders(self.altered('order_date', value))
        validate_orders(self.altered('order_date', '2024-02-29'))

    def test_22_integer_types_no_bool_float_null(self):
        for field in INTEGER_FIELDS:
            for value in [True, False, 2.0, '2', None, float('nan'), float('inf')]:
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaises(ValueError):
                        validate_orders(self.altered(field, value))

    def test_23_numeric_ranges(self):
        for field, value in [('quantity', 0), ('quantity', -1),
                             ('unit_price_toman', -1), ('returned_quantity', -1)]:
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    validate_orders(self.altered(field, value))
        rows = self.altered('returned_quantity', self.rows[0]['quantity'] + 1)
        with self.assertRaises(ValueError):
            validate_orders(rows)

    def test_24_duplicate_order_ids(self):
        with self.assertRaises(ValueError):
            validate_orders(self.rows + [dict(self.rows[0])])

    def test_25_validation_and_writing_do_not_mutate(self):
        before = copy.deepcopy(self.rows)
        validate_orders(self.rows)
        write_orders_csv(self.rows, self.folder / 'out.csv')
        write_orders_json(self.rows, self.folder / 'out.json')
        self.assertEqual(self.rows, before)

    def test_26_csv_header_exact_order(self):
        headers = [[], ['bad'], list(reversed(FIELDS)),
                   list(FIELDS) + ['extra'], list(FIELDS)[:-1],
                   ['order_id'] * len(FIELDS)]
        for fields in headers:
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    read_orders_csv(self.write_csv_text(','.join(fields) + '\n'))

    def test_27_csv_short_and_extra_fields(self):
        for record in ['A01,2025-01-01,Tools,2,100',
                       'A01,2025-01-01,Tools,2,100,0,extra']:
            with self.subTest(record=record):
                path = self.write_csv_text(','.join(FIELDS) + '\n' + record + '\n')
                with self.assertRaises(ValueError):
                    read_orders_csv(path)

    def test_28_csv_bad_and_missing_numeric_values(self):
        for field in INTEGER_FIELDS:
            for value in ['', 'NA', '2.0', '1,000']:
                with self.subTest(field=field, value=value):
                    row = dict(self.rows[0]); row[field] = value
                    path = self.folder / 'bad.csv'
                    with path.open('w', encoding='utf-8', newline='') as target:
                        writer = csv.DictWriter(target, fieldnames=FIELDS)
                        writer.writeheader(); writer.writerow(row)
                    with self.assertRaises(ValueError):
                        read_orders_csv(path)

    def test_29_bom_accepted(self):
        for writer, reader in [(write_orders_csv, read_orders_csv),
                               (write_orders_json, read_orders_json)]:
            path = self.folder / writer.__name__
            writer(self.rows, path)
            path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes())
            self.assertEqual(reader(path), self.rows)

    def test_30_csv_crlf_and_blank_lines(self):
        path = self.folder / 'input.csv'
        write_orders_csv(self.rows, path)
        lines = path.read_text().splitlines()
        path.write_bytes(('\r\n\r\n'.join(lines) + '\r\n').encode('utf-8'))
        self.assertEqual(read_orders_csv(path), self.rows)

    def test_31_csv_whitespace_numeric_policy(self):
        row = dict(self.rows[0]); row['quantity'] = ' +3 '
        row['returned_quantity'] = ' 0 '; row['unit_price_toman'] = ' +100 '
        path = self.folder / 'input.csv'
        with path.open('x', encoding='utf-8', newline='') as target:
            writer = csv.DictWriter(target, fieldnames=FIELDS)
            writer.writeheader(); writer.writerow(row)
        actual = read_orders_csv(path)[0]
        self.assertEqual([actual[f] for f in INTEGER_FIELDS], [3, 100, 0])

    def test_32_csv_bad_quotes(self):
        path = self.write_csv_text(','.join(FIELDS) + '\nA01,"unfinished\n')
        with self.assertRaises(csv.Error):
            read_orders_csv(path)

    def test_33_json_malformed_extra_document(self):
        for value in ["{'x': 2}", '{}{}', '[1,]', '']:
            path = self.folder / 'input.json'
            path.write_text(value, encoding='utf-8')
            with self.subTest(value=value):
                with self.assertRaises(json.JSONDecodeError):
                    read_orders_json(path)

    def test_34_json_wrong_root_and_schema(self):
        for value in [{}, [1], [dict(self.rows[0], quantity=True)],
                      [dict(self.rows[0], quantity=2.0)],
                      [dict(self.rows[0], quantity=None)]]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    read_orders_json(self.write_json_value(value))

    def test_35_duplicate_json_keys_known_limit(self):
        text = json.dumps([self.rows[0]])
        old = '"quantity": ' + str(self.rows[0]['quantity'])
        text = text.replace(old, '"quantity": 99, ' + old)
        path = self.folder / 'duplicate.json'
        path.write_text(text, encoding='utf-8')
        self.assertEqual(read_orders_json(path), [self.rows[0]])

    def test_36_special_characters_identifiers_and_unicode(self):
        rows = [dict(self.rows[0], order_id='0012', category='A,B "C"\nD'),
                dict(self.rows[1], order_id='0013', category=chr(0x628) + ' A')]
        for writer, reader in [(write_orders_csv, read_orders_csv),
                               (write_orders_json, read_orders_json)]:
            path = self.folder / writer.__name__
            writer(rows, path)
            self.assertEqual(reader(path), rows)
        self.assertTrue((self.folder / 'write_orders_json').read_bytes().isascii())

    def test_37_seeded_generated_round_trips_and_totals(self):
        rng = random.Random(9)
        for n in [0, 1, 2, 17, 100]:
            with self.subTest(n=n):
                rows = []
                for i in range(n):
                    q = rng.randint(1, 9)
                    rows.append(dict(order_id=f'{i:05}', order_date='2025-01-01',
                                     category=rng.choice(['A', 'B,C', 'D"E', 'F\nG']),
                                     quantity=q, unit_price_toman=rng.randint(0, 999),
                                     returned_quantity=rng.randint(0, q)))
                for writer, reader in [(write_orders_csv, read_orders_csv),
                                       (write_orders_json, read_orders_json)]:
                    path = self.folder / (writer.__name__ + str(n))
                    writer(rows, path)
                    restored = reader(path)
                    self.assertEqual(restored, rows)
                    self.assertEqual(sum((r['quantity']-r['returned_quantity']) *
                                         r['unit_price_toman'] for r in restored),
                                     sum(r['quantity']*r['unit_price_toman'] -
                                         r['returned_quantity']*r['unit_price_toman']
                                         for r in rows))

    def test_38_file_modes_and_resource_cleanup(self):
        path = self.folder / 'mode.txt'
        path.write_text('approved', encoding='utf-8')
        with path.open('w', encoding='utf-8') as target:
            self.assertEqual(path.read_bytes(), b'')
            target.write('new')
        self.assertTrue(target.closed)
        with path.open('a', encoding='utf-8') as target:
            target.write('er')
        self.assertEqual(path.read_text(), 'newer')
        with self.assertRaises(RuntimeError):
            with path.open('r', encoding='utf-8') as source:
                raise RuntimeError('controlled')
        self.assertTrue(source.closed)
        with tempfile.TemporaryDirectory() as folder:
            cleaned = Path(folder)
        self.assertFalse(cleaned.exists())

    def test_39_exercise_write_once_and_count_edges(self):
        answers = {a['exercise']: a for a in load_catalog('answers.json')}
        namespaces = {}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(answers[9]['code'], namespaces)
        path = self.folder / 'once.txt'
        namespaces['write_once'](path, 'approved')
        with self.assertRaises(FileExistsError):
            namespaces['write_once'](path, 'new')
        self.assertEqual(path.read_text(), 'approved')
        with contextlib.redirect_stdout(io.StringIO()):
            exec(answers[11]['code'], namespaces)
        for q, r, expected in [(1, 0, True), (1, 1, True), (0, 0, False),
                               (3, False, False), (3.0, 0, False),
                               (3, -1, False), ('3', 0, False)]:
            self.assertIs(namespaces['valid_counts'](q, r), expected)

    def test_40_contextual_export_snippet(self):
        source = (ROOT / 'chapter-09-full-fa.md').read_text()
        blocks = re.findall(r'```python\n(.*?)\n```', source, re.S)
        code = next(b for b in blocks if 'my_exports' in b)
        (self.folder / 'data').mkdir()
        shutil.copy2(ROOT / 'data/orders.csv', self.folder / 'data/orders.csv')
        prefix = 'import sys; sys.path.insert(0, ' + repr(str(ROOT)) + ')\n'
        self.assertEqual(self.run_code(prefix + code), '')
        self.assertEqual(read_orders_json(self.folder / 'my_exports/orders.json'), self.rows)
        result = subprocess.run([sys.executable, '-c', prefix + code],
                                cwd=self.folder, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FileExistsError', result.stderr)

    def test_41_missing_and_wrong_encoding_inputs(self):
        for reader in [read_orders_csv, read_orders_json]:
            with self.assertRaises(FileNotFoundError):
                reader(self.folder / 'missing')
            path = self.folder / 'bad'
            path.write_bytes(b'\xff')
            with self.assertRaises(UnicodeDecodeError):
                reader(path)

    def test_42_empty_file_versus_header_only(self):
        path = self.write_csv_text('')
        with self.assertRaises(ValueError):
            read_orders_csv(path)
        path = self.write_csv_text(','.join(FIELDS) + '\n')
        self.assertEqual(read_orders_csv(path), [])

    def test_43_pure_path_not_actual_windows_execution(self):
        self.assertEqual((Path('data') / 'orders.csv').as_posix(), 'data/orders.csv')
        self.assertEqual(PureWindowsPath(r'C:\book\orders.csv').drive, 'C:')

    def test_44_narrative_module_snippets_current(self):
        text = (ROOT / 'chapter-09-full-fa.md').read_text()
        for name in ['file_io.py', 'cli.py']:
            code = (ROOT / 'order_report' / name).read_text(encoding='ascii')
            self.assertIn('```python\n' + code.rstrip() + '\n```', text)

    def test_45_json_nonfinite_policy(self):
        with self.assertRaises(ValueError):
            json.dumps({'value': float('nan')}, allow_nan=False)
        for v in [float('nan'), float('inf'), float('-inf')]:
            with self.assertRaises(ValueError):
                read_orders_json(self.write_json_value(self.altered('quantity', v)))

    def test_46_same_total_not_same_records(self):
        original = [dict(self.rows[0])]
        altered = [dict(self.rows[0], order_id='different')]
        total = lambda rs: sum(r['quantity']*r['unit_price_toman'] for r in rs)
        self.assertEqual(total(original), total(altered))
        self.assertNotEqual(original, altered)


if __name__ == '__main__':
    unittest.main(verbosity=2)
