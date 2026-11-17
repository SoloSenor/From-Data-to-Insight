"""Regression tests for chapter 08; not a full production validator."""
import ast
from contextlib import redirect_stdout
from copy import deepcopy
import importlib
import inspect
import io
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from order_report.metrics import enrich_orders, group_totals, order_amounts
from order_report.reporting import build_report, check_unique_ids, format_report, rank_groups
from order_report.sample_data import make_orders

CATALOG = json.loads((ROOT / "examples/catalog.json").read_text(encoding="utf-8"))
ANSWERS = json.loads((ROOT / "examples/answers.json").read_text(encoding="utf-8"))
TEXT = (ROOT / "chapter-08-full-fa.txt").read_text(encoding="utf-8")
EXPECTED = ("orders 12\ngross_toman 5020000\nrefund_toman 1430000\n"
            "retained_toman 3590000\nDigital 2450000 68.25%\n"
            "Books 690000 19.22%\nStationery 450000 12.53%\n")


def oracle(rows):
    """Use per-unit addition instead of the implementation multiplication."""
    gross, refund = 0, 0
    groups = {}
    for row in rows:
        groups.setdefault(row["category"], 0)
        for i in range(row["quantity"]):
            gross += row["unit_price_toman"]
            if i < row["returned_quantity"]:
                refund += row["unit_price_toman"]
            else:
                groups[row["category"]] += row["unit_price_toman"]
    return gross, refund, groups


class Chapter08Tests(unittest.TestCase):
    def test_01_dataset_contract(self):
        rows = make_orders()
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({r["order_id"] for r in rows}), 12)
        for row in rows:
            self.assertEqual(set(row), {"order_id", "order_date", "category", "quantity",
                                       "unit_price_toman", "returned_quantity"})
            self.assertTrue(row["order_id"] and row["category"])
            for key in ("quantity", "unit_price_toman", "returned_quantity"):
                self.assertIs(type(row[key]), int)
            self.assertGreater(row["quantity"], 0)
            self.assertGreaterEqual(row["unit_price_toman"], 0)
            self.assertTrue(0 <= row["returned_quantity"] <= row["quantity"])

    def test_02_json_matches_factory(self):
        self.assertEqual(make_orders(), json.loads((ROOT / "data/orders.json").read_text()))

    def test_03_factory_independent_calls(self):
        first, second = make_orders(), make_orders()
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        for left, right in zip(first, second, strict=True):
            self.assertIsNot(left, right)
        first[0]["quantity"] = 99
        self.assertEqual(second[0]["quantity"], 2)
        self.assertEqual(make_orders()[0]["quantity"], 2)

    def test_04_amount_cases(self):
        self.assertEqual(order_amounts(2, 450000, 1), (900000, 450000, 450000))
        self.assertEqual(order_amounts(2, 450000), (900000, 0, 900000))
        self.assertEqual(order_amounts(2, 450000, 2), (900000, 900000, 0))
        self.assertEqual(order_amounts(2, 0), (0, 0, 0))

    def test_05_computations_do_not_print(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = build_report(make_orders())
            format_report(result)
            order_amounts(2, 100)
        self.assertEqual(stream.getvalue(), "")

    def test_06_enrich_no_mutation(self):
        rows = make_orders()
        before = deepcopy(rows)
        enriched = enrich_orders(rows)
        self.assertEqual(rows, before)
        for old, new in zip(rows, enriched, strict=True):
            self.assertIsNot(old, new)
        enriched[0]["quantity"] = 99
        self.assertEqual(rows, before)

    def test_07_documented_shallow_copy(self):
        rows = [dict(make_orders()[0], tags=["new"])]
        enriched = enrich_orders(rows)
        self.assertIs(enriched[0]["tags"], rows[0]["tags"])

    def test_08_group_totals(self):
        self.assertEqual(group_totals(enrich_orders(make_orders())),
                         {"Books": 690000, "Digital": 2450000, "Stationery": 450000})

    def test_09_report_totals(self):
        report = build_report(make_orders())
        self.assertEqual(report["order_count"], 12)
        self.assertEqual(report["gross_toman"], 5020000)
        self.assertEqual(report["refund_toman"], 1430000)
        self.assertEqual(report["retained_toman"], 3590000)

    def test_10_ranking_and_shares(self):
        groups = build_report(make_orders())["groups"]
        self.assertEqual([g["category"] for g in groups], ["Digital", "Books", "Stationery"])
        self.assertAlmostEqual(sum(g["share"] for g in groups), 1)
        for group in groups:
            self.assertEqual(group["share"], group["retained_toman"] / 3590000)

    def test_11_empty_report(self):
        result = build_report([])
        self.assertEqual(result, {"order_count": 0, "gross_toman": 0, "refund_toman": 0,
                                 "retained_toman": 0, "groups": [], "rows": []})
        self.assertEqual(format_report(result),
                         "orders 0\ngross_toman 0\nrefund_toman 0\nretained_toman 0")

    def test_12_all_returned(self):
        rows = make_orders()
        for row in rows:
            row["returned_quantity"] = row["quantity"]
        result = build_report(rows)
        self.assertEqual(result["retained_toman"], 0)
        self.assertTrue(all(g["share"] is None for g in result["groups"]))
        self.assertEqual([g["category"] for g in result["groups"]],
                         ["Books", "Digital", "Stationery"])
        self.assertIn("Books 0 NA", format_report(result))

    def test_13_zero_price_is_not_full_return(self):
        rows = make_orders()
        for row in rows:
            row["unit_price_toman"] = 0
            row["returned_quantity"] = 0
        result = build_report(rows)
        self.assertEqual(result["retained_toman"], 0)
        self.assertTrue(all(g["share"] is None for g in result["groups"]))
        self.assertTrue(all(r["returned_quantity"] < r["quantity"] for r in rows))

    def test_14_zero_group_positive_denominator(self):
        self.assertEqual(rank_groups({"A": 0, "B": 10}, 10),
                         [{"category": "B", "retained_toman": 10, "share": 1},
                          {"category": "A", "retained_toman": 0, "share": 0}])

    def test_15_tie_break(self):
        self.assertEqual([g["category"] for g in rank_groups({"Z": 10, "A": 10}, 20)],
                         ["A", "Z"])

    def test_16_duplicate_id_rejected(self):
        row = make_orders()[0]
        for function in (check_unique_ids, build_report):
            with self.assertRaisesRegex(ValueError, "Duplicate order_id"):
                function([row, row.copy()])
        self.assertIsNone(check_unique_ids(make_orders()))

    def test_17_report_preserves_input(self):
        rows = make_orders()
        before = deepcopy(rows)
        result = build_report(rows)
        self.assertEqual(rows, before)
        self.assertEqual([r["order_id"] for r in result["rows"]],
                         [r["order_id"] for r in rows])
        result["rows"][0]["quantity"] = 99
        self.assertEqual(rows, before)

    def test_18_order_independence(self):
        rows = make_orders()
        first, second = build_report(rows), build_report(rows[::-1])
        for key in ("gross_toman", "refund_toman", "retained_toman", "groups"):
            self.assertEqual(first[key], second[key])
        self.assertEqual(second["rows"][0]["order_id"], "O012")

    def test_19_independent_small_random_oracle(self):
        rng = random.Random(803)
        rows = []
        for i in range(150):
            quantity = rng.randint(1, 8)
            rows.append({"order_id": f"R{i}", "order_date": "2026-10-01",
                         "category": rng.choice(["A", "B", "C", "D"]),
                         "quantity": quantity, "unit_price_toman": rng.randint(0, 1000),
                         "returned_quantity": rng.randint(0, quantity)})
        before = deepcopy(rows)
        gross, refund, totals = oracle(rows)
        result = build_report(rows)
        self.assertEqual(result["gross_toman"], gross)
        self.assertEqual(result["refund_toman"], refund)
        self.assertEqual(result["retained_toman"], sum(totals.values()))
        self.assertEqual({g["category"]: g["retained_toman"] for g in result["groups"]}, totals)
        self.assertEqual(rows, before)

    def test_20_each_sample_row_oracle(self):
        for row in make_orders():
            gross, refund, totals = oracle([row])
            self.assertEqual(order_amounts(row["quantity"], row["unit_price_toman"],
                                          row["returned_quantity"]),
                             (gross, refund, sum(totals.values())))

    def test_21_format_exact_output(self):
        text = format_report(build_report(make_orders()))
        self.assertEqual(text + "\n", EXPECTED)
        self.assertFalse(text.endswith("\n"))
        self.assertTrue(text.isascii())

    def test_22_display_filter_preserves_denominator(self):
        report = build_report(make_orders())
        before = deepcopy(report)
        text = format_report(report, minimum_toman=500000)
        self.assertEqual(text + "\n", EXPECTED.replace("Stationery 450000 12.53%\n", ""))
        self.assertEqual(report, before)
        self.assertEqual(len(report["groups"]), 3)
        self.assertLess(sum(g["share"] for g in report["groups"]
                            if g["retained_toman"] >= 500000), 1)

    def test_23_display_filter_boundaries(self):
        report = build_report(make_orders())
        self.assertIn("Books 690000", format_report(report, minimum_toman=690000))
        self.assertNotIn("Books 690000", format_report(report, minimum_toman=690001))
        self.assertEqual(len(format_report(report, minimum_toman=9999999).splitlines()), 4)
        with self.assertRaises(TypeError):
            format_report(report, 500000)

    def test_24_all_examples_exact(self):
        self.assertEqual(len(CATALOG), 30)
        namespace = {}
        for example in CATALOG:
            with self.subTest(example=example["id"]):
                stream = io.StringIO()
                with redirect_stdout(stream):
                    exec(compile(example["code"], example["id"], "exec"), namespace)
                self.assertEqual(stream.getvalue(), example["output"])

    def test_25_all_coding_answers_exact(self):
        self.assertEqual(len(ANSWERS), 8)
        namespace = {"orders": make_orders()}
        for answer in ANSWERS:
            with self.subTest(exercise=answer["id"]):
                stream = io.StringIO()
                with redirect_stdout(stream):
                    exec(compile(answer["code"], answer["id"], "exec"), namespace)
                self.assertEqual(stream.getvalue(), answer["output"])

    def test_26_intentional_errors(self):
        cases = json.loads((ROOT / "examples/intentional-errors.json").read_text())
        import builtins
        self.assertEqual(len(cases), 6)
        for case in cases:
            with self.subTest(error=case["id"]):
                with self.assertRaises(getattr(builtins, case["exception"])):
                    exec(compile(case["code"], case["id"], "exec"), {})

    def test_27_print_and_mutable_defaults(self):
        namespace = {}
        for number in ("02", "16", "17"):
            code = next(item["code"] for item in CATALOG if item["id"] == number)
            with redirect_stdout(io.StringIO()):
                exec(code, namespace)
        with redirect_stdout(io.StringIO()):
            self.assertIsNone(namespace["show_amount"](2, 100))
        first, second = namespace["remembered"]("X"), namespace["remembered"]("Y")
        self.assertIsNot(first, second)
        self.assertEqual(second, ["Y"])

    def test_28_type_hints_not_validation(self):
        namespace = {}
        with redirect_stdout(io.StringIO()):
            exec(next(i["code"] for i in CATALOG if i["id"] == "20"), namespace)
        self.assertEqual(namespace["identity_number"]("text"), "text")
        self.assertEqual(namespace["identity_number"].__annotations__,
                         {"value": int, "return": int})
        self.assertEqual(order_amounts(2, -1), (-2, 0, -2))

    def test_29_text_matches_material(self):
        self.assertEqual(TEXT, (ROOT / "chapter-08-full-fa.md").read_text(encoding="utf-8"))
        for item in CATALOG + ANSWERS:
            self.assertIn(item["code"], TEXT)
            self.assertIn(item["output"], TEXT)
        for name in ("metrics.py", "reporting.py", "cli.py", "__main__.py"):
            self.assertIn((ROOT / "order_report" / name).read_text(), TEXT)
        self.assertIn((ROOT / "run_analysis.py").read_text(), TEXT)

    def test_30_ascii_compilation_and_fences(self):
        for path in ROOT.rglob("*.py"):
            code = path.read_text(encoding="utf-8")
            self.assertTrue(code.isascii(), str(path))
            compile(code, str(path), "exec")
        for item in CATALOG + ANSWERS:
            self.assertTrue(item["code"].isascii())
            self.assertTrue(item["output"].isascii())
        for path in ROOT.rglob("*"):
            if path.suffix in (".md", ".txt"):
                text = path.read_text(encoding="utf-8")
                for block in re.findall(r"```[^\n]*\n(.*?)```", text, re.S):
                    self.assertTrue(block.isascii(), str(path))

    def test_31_notebook_published_unexecuted(self):
        import nbformat
        nb = nbformat.read(ROOT / "notebooks/08-functions-and-modules.ipynb", as_version=4)
        nbformat.validate(nb)
        cells = [c for c in nb.cells if c.cell_type == "code"]
        self.assertEqual([c.source for c in cells], [i["code"] for i in CATALOG])
        for cell in cells:
            self.assertIsNone(cell.execution_count)
            self.assertEqual(cell.outputs, [])
            self.assertTrue(cell.source.isascii())

    def test_32_example_and_answer_subprocess(self):
        for file, catalog in (("08-examples.py", CATALOG), ("08-answers.py", ANSWERS)):
            with self.subTest(file=file), tempfile.TemporaryDirectory() as cwd:
                p = subprocess.run([sys.executable, str(ROOT / "examples" / file)],
                                   cwd=cwd, capture_output=True, text=True, check=True)
                self.assertEqual(p.stdout, "".join(i["output"] for i in catalog))
                self.assertEqual(p.stderr, "")

    def test_33_runner_from_other_directory(self):
        with tempfile.TemporaryDirectory() as cwd:
            p = subprocess.run([sys.executable, str(ROOT / "run_analysis.py")],
                               cwd=cwd, capture_output=True, text=True, check=True)
        self.assertEqual(p.stdout, EXPECTED)
        self.assertEqual(p.stderr, "")

    def test_34_package_module_entrypoints(self):
        for module in ("order_report", "order_report.cli"):
            p = subprocess.run([sys.executable, "-m", module], cwd=ROOT,
                               capture_output=True, text=True, check=True)
            self.assertEqual(p.stdout, EXPECTED)
            self.assertEqual(p.stderr, "")

    def test_35_import_has_no_report_side_effect(self):
        names = ["order_report", "order_report.metrics", "order_report.reporting",
                 "order_report.sample_data", "order_report.cli",
                 "order_report.__main__", "run_analysis"]
        code = "; ".join("import " + name for name in names)
        before = {p.relative_to(ROOT): p.read_bytes() for d in ("outputs", "data")
                  for p in (ROOT / d).rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        p = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                           capture_output=True, text=True, check=True)
        self.assertEqual(p.stdout, "")
        self.assertEqual(p.stderr, "")
        after = {p.relative_to(ROOT): p.read_bytes() for d in ("outputs", "data")
                 for p in (ROOT / d).rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        self.assertEqual(before, after)

    def test_36_stdlib_runtime_dependencies_and_directions(self):
        for path in (ROOT / "order_report").glob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertIn(alias.name.split(".")[0], sys.stdlib_module_names)
                elif isinstance(node, ast.ImportFrom):
                    if not node.level:
                        self.assertIn(node.module.split(".")[0], sys.stdlib_module_names)
        imports = [node.module for node in ast.walk(ast.parse(
            (ROOT / "order_report/reporting.py").read_text())) if isinstance(node, ast.ImportFrom)]
        self.assertEqual(imports, ["metrics"])
        metrics = ast.parse((ROOT / "order_report/metrics.py").read_text())
        self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(metrics)))

    def test_37_readme_and_summary_links(self):
        for file in ("README.md", "chapter-08-summary-fa.md"):
            for target in re.findall(r"\]\(([^)]+)\)", (ROOT / file).read_text()):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((ROOT / target).is_file(), (file, target))

    def test_38_module_use_snippet(self):
        code = ("from order_report.reporting import build_report, format_report\n"
                "from order_report.sample_data import make_orders\n\n"
                "report = build_report(make_orders())\n"
                "print(format_report(report, minimum_toman=500000))\n")
        self.assertIn(code, TEXT)
        p = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                           capture_output=True, text=True, check=True)
        self.assertEqual(p.stdout, EXPECTED.replace("Stationery 450000 12.53%\n", ""))
        self.assertEqual(p.stderr, "")

    def test_39_published_reference_outputs(self):
        report = build_report(make_orders())
        self.assertEqual(json.loads((ROOT / "outputs/report.json").read_text()), report)
        self.assertEqual((ROOT / "outputs/report.txt").read_text(), EXPECTED)
        self.assertEqual((ROOT / "outputs/report-filtered.txt").read_text(),
                         format_report(report, minimum_toman=500000) + "\n")

    def test_40_public_signatures_and_docstrings(self):
        signature = inspect.signature(format_report)
        parameter = signature.parameters["minimum_toman"]
        self.assertEqual(parameter.kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertEqual(parameter.default, 0)
        for function in (order_amounts, enrich_orders, group_totals, check_unique_ids,
                         rank_groups, build_report, format_report, make_orders):
            self.assertTrue(function.__doc__)
            self.assertTrue(function.__doc__.isascii())
            self.assertIn("return", function.__annotations__)


if __name__ == "__main__":
    unittest.main(verbosity=2)
