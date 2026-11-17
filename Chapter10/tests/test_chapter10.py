"""Executable contracts, not a proof for arbitrary inputs or platforms."""
from contextlib import closing
import csv
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from order_report.source import iter_orders_csv
from order_report.pipeline import ReportAccumulator, summarize_orders, format_report
from order_report.validation import FIELDS, validate_orders

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = json.loads((ROOT / "data/orders.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "examples/catalog.json").read_text(encoding="utf-8"))
SOLUTIONS = json.loads((ROOT / "examples/solutions.json").read_text(encoding="utf-8"))
ERRORS = json.loads((ROOT / "examples/intentional-errors.json").read_text(encoding="utf-8"))


class TeachingCases(unittest.TestCase):
    pass


def attach_stdout_case(item, prefix):
    def check(self):
        process = subprocess.run([sys.executable, "-c", item["code"]],
                                 cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        self.assertEqual(process.stdout, item["output"])
        self.assertTrue(item["code"].isascii())
        self.assertTrue(process.stdout.isascii())
    setattr(TeachingCases, f"test_{prefix}_{item['id']}", check)


for item in CATALOG:
    attach_stdout_case(item, "example")
for item in SOLUTIONS:
    attach_stdout_case(item, "solution")
for item in ERRORS:
    def attach_error(item):
        def check(self):
            process = subprocess.run([sys.executable, "-c", item["code"]],
                                     cwd=ROOT, capture_output=True, text=True, timeout=20)
            self.assertEqual(process.stdout, item["output"])
            if item["exception"]:
                self.assertNotEqual(process.returncode, 0)
                final_line = process.stderr.rstrip().splitlines()[-1]
                self.assertEqual(final_line.split(":", 1)[0].rsplit(".", 1)[-1], item["exception"])
            else:
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(process.stderr, "")
        setattr(TeachingCases, f"test_error_{item['id']}", check)
    attach_error(item)


class SinglePass:
    """Reject a second request for an iterator from the same iterable."""
    def __init__(self, values):
        self.values = values
        self.calls = 0

    def __iter__(self):
        self.calls += 1
        if self.calls != 1:
            raise AssertionError("A second pass was requested")
        return iter(self.values)


class WorkshopCases(unittest.TestCase):
    def csv_path(self, text):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "input.csv"
        path.write_text(text, encoding="utf-8", newline="")
        return path

    def read_all(self, path):
        with closing(iter_orders_csv(path)) as rows:
            return list(rows)

    def test_csv_matches_json_records(self):
        self.assertEqual(self.read_all(ROOT / "data/orders.csv"), REFERENCE)

    def test_reference_independent_arithmetic(self):
        report = summarize_orders(iter(REFERENCE))
        gross = sum(row["quantity"] * row["unit_price_toman"] for row in REFERENCE)
        refund = sum(row["returned_quantity"] * row["unit_price_toman"] for row in REFERENCE)
        self.assertEqual((len(REFERENCE), gross, refund), (12, 5020000, 1430000))
        self.assertEqual(report["gross_toman"], gross)
        self.assertEqual(report["refund_toman"], refund)
        self.assertEqual(report["retained_toman"], gross - refund)
        self.assertEqual(report["retained_toman"], 3590000)
        self.assertEqual(report["orders"], len(REFERENCE))

    def test_category_reference_values(self):
        report = summarize_orders(iter(REFERENCE))
        actual = {row["category"]: row["retained_toman"] for row in report["categories"]}
        self.assertEqual(actual, {"Digital": 2450000, "Books": 690000, "Stationery": 450000})
        for category, amount in actual.items():
            expected = sum((row["quantity"] - row["returned_quantity"]) * row["unit_price_toman"]
                           for row in REFERENCE if row["category"] == category)
            self.assertEqual(amount, expected)
        self.assertEqual(sum(actual.values()), report["retained_toman"])
        self.assertAlmostEqual(sum(row["share"] for row in report["categories"]), 1)

    def test_only_one_pass(self):
        source = SinglePass(REFERENCE)
        report = summarize_orders(source)
        self.assertEqual(source.calls, 1)
        self.assertEqual(report["orders"], 12)

    def test_generator_exhaustion(self):
        source = (dict(row) for row in REFERENCE)
        self.assertEqual(summarize_orders(source)["orders"], 12)
        self.assertEqual(summarize_orders(source)["orders"], 0)

    def test_empty_report(self):
        self.assertEqual(summarize_orders(iter([])),
                         {"orders": 0, "gross_toman": 0, "refund_toman": 0,
                          "retained_toman": 0, "categories": []})

    def test_all_returned_share_is_none(self):
        rows = deepcopy(REFERENCE)
        for row in rows:
            row["returned_quantity"] = row["quantity"]
        report = summarize_orders(iter(rows))
        self.assertEqual(report["retained_toman"], 0)
        self.assertTrue(all(row["share"] is None for row in report["categories"]))
        self.assertIn(" NA", format_report(report))

    def test_zero_price(self):
        row = dict(REFERENCE[0], unit_price_toman=0)
        self.assertEqual(summarize_orders(iter([row]))["retained_toman"], 0)

    def test_tie_breaking(self):
        rows = [dict(REFERENCE[0], order_id="X1", category="Z", quantity=1,
                     returned_quantity=0, unit_price_toman=10),
                dict(REFERENCE[0], order_id="X2", category="A", quantity=1,
                     returned_quantity=0, unit_price_toman=10)]
        self.assertEqual([row["category"] for row in summarize_orders(iter(rows))["categories"]],
                         ["A", "Z"])

    def test_duplicate_across_stream(self):
        with self.assertRaises(ValueError):
            summarize_orders(iter(REFERENCE + [dict(REFERENCE[0])]))

    def test_duplicate_does_not_update_state(self):
        accumulator = ReportAccumulator()
        accumulator.add(dict(REFERENCE[0]))
        before = accumulator.snapshot()
        with self.assertRaises(ValueError):
            accumulator.add(dict(REFERENCE[0]))
        self.assertEqual(accumulator.snapshot(), before)

    def test_invalid_row_does_not_update_state(self):
        accumulator = ReportAccumulator()
        accumulator.add(dict(REFERENCE[0]))
        before = accumulator.snapshot()
        with self.assertRaises(ValueError):
            accumulator.add(dict(REFERENCE[1], quantity=-1))
        self.assertEqual(accumulator.snapshot(), before)

    def test_independent_instances(self):
        first, second = ReportAccumulator(), ReportAccumulator()
        first.add(dict(REFERENCE[0]))
        self.assertEqual(second.snapshot()["orders"], 0)
        self.assertEqual(second.snapshot()["categories"], [])

    def test_snapshot_does_not_alias(self):
        accumulator = ReportAccumulator()
        accumulator.add(dict(REFERENCE[0]))
        expected = accumulator.snapshot()
        external = accumulator.snapshot()
        external["categories"][0]["retained_toman"] = -1
        external["categories"].append({"category": "wrong"})
        external["orders"] = -1
        self.assertEqual(accumulator.snapshot(), expected)

    def test_input_not_mutated(self):
        rows = deepcopy(REFERENCE)
        summarize_orders(iter(rows))
        self.assertEqual(rows, REFERENCE)

    def test_missing_file_error_is_delayed(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        source = iter_orders_csv(Path(directory.name) / "missing.csv")
        self.addCleanup(source.close)
        with self.assertRaises(FileNotFoundError):
            next(source)

    def test_close_after_first_row(self):
        source = iter_orders_csv(ROOT / "data/orders.csv")
        next(source)
        frame = source.gi_frame
        handle = frame.f_locals["source"]
        self.assertFalse(handle.closed)
        source.close()
        self.assertTrue(handle.closed)
        self.assertEqual(list(source), [])

    def test_close_after_complete_iteration(self):
        source = iter_orders_csv(ROOT / "data/orders.csv")
        next(source)
        handle = source.gi_frame.f_locals["source"]
        list(source)
        self.assertTrue(handle.closed)

    def test_close_after_late_domain_error(self):
        original = (ROOT / "data/orders.csv").read_text()
        records = list(csv.reader(original.splitlines()))
        records[-1][3] = "-1"
        import io
        target = io.StringIO(newline="")
        csv.writer(target, lineterminator="\n").writerows(records)
        source = iter_orders_csv(self.csv_path(target.getvalue()))
        next(source)
        handle = source.gi_frame.f_locals["source"]
        with self.assertRaises(ValueError):
            with closing(source):
                summarize_orders(source)
        self.assertTrue(handle.closed)

    def test_header_only_is_valid_empty(self):
        self.assertEqual(self.read_all(self.csv_path(",".join(FIELDS) + "\n")), [])

    def test_empty_file_is_not_header(self):
        with self.assertRaises(ValueError):
            self.read_all(self.csv_path(""))

    def test_wrong_header(self):
        with self.assertRaises(ValueError):
            self.read_all(self.csv_path("wrong,header\n1,2\n"))

    def test_extra_cell(self):
        with self.assertRaises(ValueError):
            self.read_all(self.csv_path(",".join(FIELDS) + "\nX,2024-01-01,A,1,2,0,extra\n"))

    def test_missing_cell(self):
        with self.assertRaises(ValueError):
            self.read_all(self.csv_path(",".join(FIELDS) + "\nX,2024-01-01,A,1,2\n"))

    def test_nonnumeric_cell(self):
        with self.assertRaises(ValueError):
            self.read_all(self.csv_path(",".join(FIELDS) + "\nX,2024-01-01,A,wrong,2,0\n"))

    def test_unclosed_quote(self):
        with self.assertRaises(csv.Error):
            self.read_all(self.csv_path(",".join(FIELDS) + '\nX,2024-01-01,"A,1,2,0\n'))

    def test_utf8_bom(self):
        path = self.csv_path("\ufeff" + (ROOT / "data/orders.csv").read_text())
        self.assertEqual(self.read_all(path), REFERENCE)

    def test_quoted_category_comma_and_newline(self):
        path = self.csv_path(",".join(FIELDS) + '\nX,2024-01-01,"A,B\nC",1,2,0\n')
        rows = self.read_all(path)
        self.assertEqual(rows[0]["category"], "A,B\nC")
        self.assertEqual(summarize_orders(iter(rows))["retained_toman"], 2)

    def test_numeric_whitespace_and_sign(self):
        path = self.csv_path(",".join(FIELDS) + "\nX,2024-01-01,A, +1 , 2 ,0\n")
        report = summarize_orders(iter(self.read_all(path)))
        self.assertEqual(report["retained_toman"], 2)

    def test_parser_alone_is_not_domain_validator(self):
        path = self.csv_path(",".join(FIELDS) + "\nX,2024-01-01,A,-1,2,0\n")
        rows = self.read_all(path)
        self.assertEqual(rows[0]["quantity"], -1)
        with self.assertRaises(ValueError):
            summarize_orders(iter(rows))

    def test_blank_physical_lines(self):
        text = (ROOT / "data/orders.csv").read_text()
        self.assertEqual(self.read_all(self.csv_path(text + "\n\n")), REFERENCE)

    def test_imports_are_quiet_and_do_not_need_data(self):
        code = "import order_report.source, order_report.pipeline, order_report.cli"
        result = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_script_from_other_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ROOT / "run_analysis.py")],
                                    cwd=directory, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (ROOT / "outputs/report.txt").read_text())

    def test_module_entry(self):
        result = subprocess.run([sys.executable, "-m", "order_report"], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (ROOT / "outputs/report.txt").read_text())

    def test_all_python_files_ascii_and_compile(self):
        for path in ROOT.rglob("*.py"):
            with self.subTest(file=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.isascii())
                compile(text, str(path), "exec")

    def test_all_markdown_fences_ascii(self):
        for path in ROOT.rglob("*.md"):
            inside = False
            for line in path.read_text().splitlines():
                if line.startswith("```"):
                    inside = not inside
                elif inside:
                    self.assertTrue(line.isascii(), str(path))
            self.assertFalse(inside, str(path))

    def test_catalog_coverage_and_notebook_ascii(self):
        import nbformat
        nb = nbformat.read(ROOT / "notebooks/10-language-tools.ipynb", as_version=4)
        cells = [cell for cell in nb.cells if cell.cell_type == "code"]
        self.assertEqual(len(cells), 30)
        for cell, item in zip(cells, CATALOG, strict=True):
            self.assertEqual(cell.source, item["code"])
            self.assertTrue(cell.source.isascii())
        self.assertEqual(len(SOLUTIONS), 12)
        self.assertEqual(len(ERRORS), 8)


# Each mutation is an independent reported test, not only a subtest.
INVALID_VALUES = [
    ("quantity", True), ("quantity", 1.0), ("quantity", 0),
    ("quantity", -1), ("unit_price_toman", -1),
    ("unit_price_toman", False), ("returned_quantity", -1),
    ("returned_quantity", 999), ("returned_quantity", 0.0),
    ("order_date", "2024-02-30"), ("order_date", "20240101"),
    ("order_date", " 2024-01-01"), ("order_id", " "),
    ("order_id", " X"), ("category", "A "), ("category", ""),
    ("category", 2),
]
for index, (field, value) in enumerate(INVALID_VALUES, start=1):
    def attach_invalid(index, field, value):
        def check(self):
            with self.assertRaises(ValueError):
                summarize_orders(iter([dict(REFERENCE[0], **{field: value})]))
        setattr(WorkshopCases, f"test_invalid_value_{index:02d}", check)
    attach_invalid(index, field, value)


class SchemaCases(unittest.TestCase):
    def test_missing_schema_key(self):
        row = dict(REFERENCE[0]); del row["category"]
        with self.assertRaises(ValueError):
            summarize_orders(iter([row]))

    def test_extra_schema_key(self):
        with self.assertRaises(ValueError):
            summarize_orders(iter([dict(REFERENCE[0], extra=1)]))

    def test_non_dict_row(self):
        with self.assertRaises(ValueError):
            summarize_orders(iter([None]))

    def test_legacy_validator_requires_list(self):
        with self.assertRaises(ValueError):
            validate_orders(iter(REFERENCE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
