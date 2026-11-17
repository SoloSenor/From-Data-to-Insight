"""Regression tests for the published chapter and its trusted-input workshop."""
import contextlib
from copy import deepcopy
import io
import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis import build_report, index_unique
from data.sample_orders import orders

CATALOG = json.loads((ROOT / "examples/catalog.json").read_text(encoding="utf-8"))
ANSWERS = json.loads((ROOT / "examples/answers.json").read_text(encoding="ascii"))
TEXT = (ROOT / "chapter-07-full-fa.txt").read_text(encoding="utf-8")


def oracle(rows):
    """Deliberately sum unit prices one unit at a time for small valid inputs."""
    totals = {}
    gross = 0
    refunds = 0
    for row in rows:
        group = row["category"]
        totals.setdefault(group, 0)
        for unit in range(row["quantity"]):
            gross += row["unit_price_toman"]
            if unit < row["returned_quantity"]:
                refunds += row["unit_price_toman"]
            else:
                totals[group] += row["unit_price_toman"]
    return gross, refunds, totals


class Chapter07Tests(unittest.TestCase):
    def test_01_dataset_structure(self):
        self.assertEqual(len(orders), 12)
        fields = {"order_id", "order_date", "category", "quantity",
                  "unit_price_toman", "returned_quantity"}
        for row in orders:
            self.assertEqual(set(row), fields)
            self.assertTrue(row["order_id"])
            self.assertTrue(row["category"])
            self.assertGreater(row["quantity"], 0)
            self.assertGreaterEqual(row["unit_price_toman"], 0)
            self.assertTrue(0 <= row["returned_quantity"] <= row["quantity"])
            for name in ("quantity", "unit_price_toman", "returned_quantity"):
                self.assertIs(type(row[name]), int)
        self.assertEqual(len({r["order_id"] for r in orders}), 12)

    def test_02_dataset_literal_matches_json(self):
        self.assertEqual(orders, json.loads((ROOT / "data/orders.json").read_text()))

    def test_03_fixed_totals(self):
        report = build_report(orders)
        self.assertEqual(report["order_count"], 12)
        self.assertEqual(report["gross_toman"], 5020000)
        self.assertEqual(report["refund_toman"], 1430000)
        self.assertEqual(report["retained_toman"], 3590000)

    def test_04_fixed_group_ranking(self):
        report = build_report(orders)
        self.assertEqual([(g["category"], g["retained_toman"]) for g in report["groups"]],
                         [("Digital", 2450000), ("Books", 690000), ("Stationery", 450000)])

    def test_05_shares(self):
        groups = build_report(orders)["groups"]
        for group in groups:
            self.assertAlmostEqual(group["share"], group["retained_toman"] / 3590000)
        self.assertAlmostEqual(sum(g["share"] for g in groups), 1.0)

    def test_06_every_row_independent_oracle(self):
        report = build_report(orders)
        for source, computed in zip(orders, report["rows"], strict=True):
            gross, refund, amounts = oracle([source])
            self.assertEqual(computed["gross_toman"], gross)
            self.assertEqual(computed["refund_toman"], refund)
            self.assertEqual(computed["retained_toman"], amounts[source["category"]])

    def test_07_no_input_mutation(self):
        source = deepcopy(orders)
        before = deepcopy(source)
        result = build_report(source)
        self.assertEqual(source, before)
        for original, returned in zip(source, result["rows"], strict=True):
            self.assertIsNot(original, returned)
        result["rows"][0]["quantity"] = 100
        self.assertEqual(source, before)

    def test_08_empty_input(self):
        result = build_report([])
        self.assertEqual(result, {"order_count": 0, "gross_toman": 0,
                         "refund_toman": 0, "retained_toman": 0, "groups": [], "rows": []})
        self.assertEqual(index_unique([]), {})

    def test_09_all_returned(self):
        source = deepcopy(orders)
        for row in source:
            row["returned_quantity"] = row["quantity"]
        result = build_report(source)
        self.assertEqual(result["retained_toman"], 0)
        self.assertEqual(len(result["groups"]), 3)
        self.assertTrue(all(g["share"] is None for g in result["groups"]))
        self.assertEqual([g["category"] for g in result["groups"]],
                         ["Books", "Digital", "Stationery"])

    def test_10_zero_price_not_full_return(self):
        source = deepcopy(orders)
        for row in source:
            row["unit_price_toman"] = 0
            row["returned_quantity"] = 0
        result = build_report(source)
        self.assertEqual(result["retained_toman"], 0)
        self.assertTrue(all(g["share"] is None for g in result["groups"]))
        self.assertFalse(any(r["returned_quantity"] == r["quantity"] for r in source))

    def test_11_added_order(self):
        source = deepcopy(orders)
        source.append({"order_id": "O013", "order_date": "2026-10-07",
                       "category": "Books", "quantity": 2,
                       "unit_price_toman": 50000, "returned_quantity": 0})
        result = build_report(source)
        self.assertEqual(result["order_count"], 13)
        self.assertEqual(result["retained_toman"], 3690000)
        self.assertEqual({g["category"]:g["retained_toman"] for g in result["groups"]}["Books"],790000)

    def test_12_reordered_input(self):
        forward, backward = build_report(orders), build_report(orders[::-1])
        self.assertEqual(forward["groups"], backward["groups"])
        self.assertEqual(backward["rows"][0]["order_id"], "O012")

    def test_13_tie_break(self):
        source = [dict(orders[0], order_id="X", category="Z", quantity=1,
                       returned_quantity=0, unit_price_toman=10),
                  dict(orders[0], order_id="Y", category="A", quantity=1,
                       returned_quantity=0, unit_price_toman=10)]
        self.assertEqual([g["category"] for g in build_report(source)["groups"]], ["A", "Z"])

    def test_14_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate order_id"):
            build_report([orders[0], orders[0].copy()])
        with self.assertRaises(ValueError):
            index_unique([orders[0], orders[0]])

    def test_15_index_references_originals(self):
        source = deepcopy(orders)
        index = index_unique(source)
        self.assertIs(index["O001"], source[0])
        index["O001"]["quantity"] = 99
        self.assertEqual(source[0]["quantity"], 99)

    def test_16_random_small_valid_orders(self):
        rng = random.Random(703)
        source = []
        for i in range(120):
            quantity = rng.randint(1, 9)
            source.append({"order_id": f"R{i:03}", "order_date": "2026-10-01",
                           "category": rng.choice(["A", "B", "C", "D"]),
                           "quantity": quantity, "unit_price_toman": rng.randint(0, 10000),
                           "returned_quantity": rng.randint(0, quantity)})
        before = deepcopy(source)
        gross, refund, totals = oracle(source)
        result = build_report(source)
        self.assertEqual(source, before)
        self.assertEqual(result["gross_toman"], gross)
        self.assertEqual(result["refund_toman"], refund)
        self.assertEqual(result["retained_toman"], sum(totals.values()))
        self.assertEqual({g["category"]:g["retained_toman"] for g in result["groups"]},totals)

    def test_17_full_and_partial_returns(self):
        full = [r["order_id"] for r in orders if r["returned_quantity"] == r["quantity"]]
        partial = [r["order_id"] for r in orders if 0 < r["returned_quantity"] < r["quantity"]]
        self.assertEqual(full, ["O004", "O011"])
        self.assertEqual(partial, ["O003", "O005", "O010"])
        self.assertEqual(sum(r["quantity"] for r in orders), 27)
        self.assertEqual(sum(r["returned_quantity"] for r in orders), 5)

    def test_18_copy_semantics(self):
        source = [{"tags": ["new"]}]
        alias = source
        shallow = source.copy()
        row_copy = [row.copy() for row in source]
        deep = deepcopy(source)
        source[0]["tags"].append("checked")
        self.assertIs(alias, source)
        self.assertIsNot(shallow, source)
        self.assertEqual(row_copy[0]["tags"], ["new", "checked"])
        self.assertEqual(deep[0]["tags"], ["new"])

    def test_19_zip_lazy_strict_and_exhaustion(self):
        pairs = zip([1,2], [3], strict=True)
        self.assertEqual(next(pairs), (1,3))
        with self.assertRaises(ValueError):
            next(pairs)
        pairs = zip([1,2], [3])
        self.assertEqual(list(pairs), [(1,3)])
        self.assertEqual(list(pairs), [])

    def test_20_stable_sort_and_record_sharing(self):
        result = sorted(orders, key=lambda r:r["quantity"], reverse=True)
        self.assertEqual([r["order_id"] for r in result[:4]], ["O003","O009","O006","O007"])
        self.assertIs(result[0], orders[2])
        self.assertEqual(orders[0]["order_id"], "O001")

    def test_21_silent_logic_bugs(self):
        numbers = [0,0,1]
        for value in numbers:
            if value == 0:
                numbers.remove(value)
        self.assertEqual(numbers, [0,1])
        buckets = dict.fromkeys(["Books","Digital"], [])
        buckets["Books"].append("O001")
        self.assertEqual(buckets["Digital"], ["O001"])

    def test_22_all_30_examples_exact(self):
        namespace = {}
        self.assertEqual(len(CATALOG),30)
        for item in CATALOG:
            with self.subTest(example=item["id"]):
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    exec(compile(item["code"], item["id"], "exec"),namespace)
                self.assertEqual(stream.getvalue(), item["output"])

    def test_23_all_8_answers_exact(self):
        self.assertEqual(len(ANSWERS),8)
        for item in ANSWERS:
            with self.subTest(answer=item["id"]):
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    exec(item["code"], {"orders":deepcopy(orders)})
                self.assertEqual(stream.getvalue(),item["output"])

    def test_24_text_catalog_matches(self):
        for item in CATALOG + ANSWERS:
            self.assertIn('```python\n'+item["code"]+'```',TEXT)
            self.assertIn('```text\n'+item["output"]+'```',TEXT)
        self.assertIn((ROOT / "analysis.py").read_text(), TEXT)
        self.assertEqual(TEXT, (ROOT / "chapter-07-full-fa.md").read_text())

    def test_25_six_intentional_errors(self):
        errors = json.loads((ROOT / "examples/intentional-errors.json").read_text())
        classes = {"TypeError":TypeError, "ValueError":ValueError,
                   "KeyError":KeyError, "RuntimeError":RuntimeError}
        self.assertEqual(len(errors),6)
        for item in errors:
            with self.subTest(error=item["id"]):
                with self.assertRaises(classes[item["type"]]):
                    exec(item["code"],{})
                self.assertIn('```python\n'+item["code"]+'```',TEXT)

    def test_26_ascii_and_compilation(self):
        for path in ROOT.rglob("*.py"):
            source = path.read_text(encoding="ascii")
            compile(source,str(path),"exec")
        for block in re.findall(r'```[^\n]*\n(.*?)```',TEXT,re.S):
            self.assertTrue(block.isascii())
        for item in CATALOG + ANSWERS:
            self.assertTrue(item["code"].isascii())
            self.assertTrue(item["output"].isascii())

    def test_27_notebook_unexecuted_and_matches(self):
        import nbformat
        nb = nbformat.read(ROOT / "notebooks/07-data-processing-patterns.ipynb",as_version=4)
        nbformat.validate(nb)
        cells = [c for c in nb.cells if c.cell_type == "code"]
        self.assertEqual(len(cells),30)
        for cell,item in zip(cells,CATALOG,strict=True):
            self.assertEqual(cell.source,item["code"].rstrip())
            self.assertEqual(cell.metadata["example_id"],item["id"])
            self.assertIsNone(cell.execution_count)
            self.assertFalse(cell.outputs)

    def test_28_teaching_script_subprocess(self):
        result = subprocess.run([sys.executable,str(ROOT / "examples/07-examples.py")],
                                capture_output=True,text=True,check=True,cwd=tempfile.gettempdir())
        self.assertEqual(result.stdout,''.join(i["output"] for i in CATALOG))
        self.assertEqual(result.stderr, "")

    def test_29_answer_script_subprocess(self):
        result = subprocess.run([sys.executable,str(ROOT / "examples/07-answers.py")],
                                capture_output=True,text=True,check=True,cwd=tempfile.gettempdir())
        self.assertEqual(result.stdout,''.join(i["output"] for i in ANSWERS))
        self.assertEqual(result.stderr, "")

    def test_30_runner_from_other_directory(self):
        before = (ROOT / "data/orders.json").read_bytes()
        sample = (ROOT / "data/sample_orders.py").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable,str(ROOT / "run_analysis.py")],cwd=directory,
                                    capture_output=True,text=True,check=True)
        self.assertEqual(result.stdout,"orders 12\nretained_toman 3590000\nDigital 2450000\nBooks 690000\nStationery 450000\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(before,(ROOT / "data/orders.json").read_bytes())
        self.assertEqual(sample,(ROOT / "data/sample_orders.py").read_bytes())
        self.assertEqual(json.loads((ROOT / "outputs/report.json").read_text()),build_report(orders))

    def test_31_local_readme_links(self):
        for name in re.findall(r'\]\(([^)]+)\)',(ROOT / "README.md").read_text()):
            if '://' not in name and not name.startswith('#'):
                self.assertTrue((ROOT / name).is_file(),name)

    def test_32_declared_non_validator_limit(self):
        # Negative prices are outside the contract, not rejected by this workshop.
        source = [dict(orders[0], unit_price_toman=-1)]
        self.assertEqual(build_report(source)["retained_toman"],-2)
        # Nested mutable fields remain shared after a shallow row copy.
        source = [dict(orders[0], tags=["new"])]
        result = build_report(source)
        self.assertIs(result["rows"][0]["tags"],source[0]["tags"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
