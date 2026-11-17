"""Independent checks for the chapter 06 teaching package."""
import builtins
import contextlib
import csv
import io
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import analysis as pipeline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import nbformat

CATALOG = json.loads((ROOT / "examples/catalog.json").read_text())
ANSWERS = json.loads((ROOT / "examples/answer-catalog.json").read_text())


class Chapter06Tests(unittest.TestCase):
    def setUp(self):
        self.raw = pipeline.load_orders(ROOT / "data/orders.csv")
        self.orders = pipeline.add_amounts(self.raw)
        self.summary = pipeline.summarize_categories(self.orders)

    def test_01_schema_and_shape(self):
        self.assertEqual(self.raw.shape, (12, 6))
        self.assertEqual(list(self.raw.columns), pipeline.COLUMNS)
        self.assertEqual(self.raw["order_id"].nunique(), 12)
        self.assertEqual(self.raw["order_date"].min(), "2026-10-01")
        self.assertEqual(self.raw["order_date"].max(), "2026-10-06")

    def test_02_independent_csv_unit_oracle(self):
        # Use the standard library and sum one price per unit, not the pipeline.
        oracle = {}
        with (ROOT / "data/orders.csv").open(newline="") as handle:
            for row in csv.DictReader(handle):
                q = int(row["quantity"])
                r = int(row["returned_quantity"])
                p = int(row["unit_price_toman"])
                values = [sum(p for _ in range(q)),
                          sum(p for _ in range(r)),
                          sum(p for _ in range(q - r))]
                oracle[row["order_id"]] = values
        self.assertEqual(len(oracle), 12)
        for _, row in self.orders.iterrows():
            self.assertEqual([int(row[c]) for c in pipeline.AMOUNTS],
                             oracle[row["order_id"]])

    def test_03_fixed_totals(self):
        self.assertEqual(self.orders[pipeline.AMOUNTS].sum().tolist(),
                         [5020000, 1430000, 3590000])

    def test_04_fixed_group_totals(self):
        expected = {"Books": [1040000, 350000, 690000],
                    "Digital": [3500000, 1050000, 2450000],
                    "Stationery": [480000, 30000, 450000]}
        for category, values in expected.items():
            self.assertEqual(self.summary.loc[category, pipeline.AMOUNTS].tolist(),
                             values)

    def test_05_shares_and_ranking(self):
        self.assertEqual(self.summary.index.tolist(), ["Digital", "Books", "Stationery"])
        for category, amount in [("Digital", 2450000), ("Books", 690000),
                                 ("Stationery", 450000)]:
            self.assertAlmostEqual(self.summary.loc[category, "retained_share_pct"],
                                   amount * 100 / 3590000)
        self.assertAlmostEqual(self.summary["retained_share_pct"].sum(), 100)

    def test_06_mean_denominator(self):
        self.assertAlmostEqual(self.orders["retained_toman"].mean(), 3590000 / 12)
        positive = self.orders.loc[self.orders["retained_toman"] > 0]
        self.assertEqual(len(positive), 10)
        self.assertAlmostEqual(positive["retained_toman"].mean(), 359000)

    def test_07_counts_and_unit_totals(self):
        self.assertEqual(self.orders.groupby("category").size().to_dict(),
                         {"Books": 4, "Digital": 4, "Stationery": 4})
        self.assertEqual(self.orders.groupby("category")["quantity"].sum().to_dict(),
                         {"Books": 8, "Digital": 5, "Stationery": 14})
        self.assertEqual(int(self.orders["quantity"].sum()), 27)
        self.assertEqual(int(self.orders["returned_quantity"].sum()), 5)
        self.assertEqual(int((self.orders["returned_quantity"] > 0).sum()), 5)

    def test_08_full_and_partial_returns(self):
        full = self.orders["returned_quantity"] == self.orders["quantity"]
        part = ((self.orders["returned_quantity"] > 0)
                & (self.orders["returned_quantity"] < self.orders["quantity"]))
        self.assertEqual(self.orders.loc[full, "order_id"].tolist(), ["O004", "O011"])
        self.assertEqual(self.orders.loc[part, "order_id"].tolist(),
                         ["O003", "O005", "O010"])

    def test_09_inputs_not_changed(self):
        before = self.raw.copy(deep=True)
        out = pipeline.add_amounts(self.raw)
        assert_frame_equal(self.raw, before)
        before_out = out.copy(deep=True)
        pipeline.summarize_categories(out)
        assert_frame_equal(out, before_out)

    def test_10_order_invariance(self):
        reversed_summary = pipeline.summarize_categories(
            pipeline.add_amounts(self.raw.iloc[::-1]))
        assert_frame_equal(self.summary, reversed_summary)

    def test_11_all_full_returns(self):
        frame = self.raw.copy()
        frame["returned_quantity"] = frame["quantity"]
        summary = pipeline.summarize_categories(pipeline.add_amounts(frame))
        self.assertTrue((summary["retained_toman"] == 0).all())
        self.assertTrue(summary["retained_share_pct"].isna().all())

    def test_12_zero_price_is_not_full_return(self):
        frame = self.raw.iloc[:1].copy()
        frame["unit_price_toman"] = 0
        out = pipeline.add_amounts(frame)
        self.assertEqual(int(out["retained_toman"].iloc[0]), 0)
        self.assertNotEqual(int(out["quantity"].iloc[0]),
                            int(out["returned_quantity"].iloc[0]))
        summary = pipeline.summarize_categories(out)
        self.assertTrue(summary["retained_share_pct"].isna().all())

    def test_13_single_no_return(self):
        out = pipeline.add_amounts(self.raw.iloc[:1])
        summary = pipeline.summarize_categories(out)
        self.assertEqual(int(out["retained_toman"].iloc[0]), 240000)
        self.assertEqual(float(summary["retained_share_pct"].iloc[0]), 100)

    def test_14_added_order(self):
        extra = self.raw.iloc[:1].copy()
        extra["order_id"] = "O013"
        extra["quantity"] = 1
        extra["unit_price_toman"] = 100000
        frame = pd.concat([self.raw, extra], ignore_index=True)
        summary = pipeline.summarize_categories(pipeline.add_amounts(frame))
        self.assertEqual(int(summary["retained_toman"].sum()), 3690000)
        self.assertAlmostEqual(summary.loc["Books", "retained_share_pct"],
                               790000 / 3690000 * 100)

    def test_15_random_valid_unit_oracle(self):
        rng = random.Random(206)
        rows = []
        expected = {c: [0, 0, 0] for c in ["Books", "Digital", "Stationery"]}
        for i in range(120):
            q = rng.randint(1, 15)
            r = rng.randint(0, q)
            p = rng.randint(0, 1000000)
            category = rng.choice(list(expected))
            rows.append([f"T{i:03}", "2026-10-01", category, q, p, r])
            for k, n in enumerate([q, r, q-r]):
                expected[category][k] += sum(p for _ in range(n))
        frame = pd.DataFrame(rows, columns=pipeline.COLUMNS)
        summary = pipeline.summarize_categories(pipeline.add_amounts(frame))
        for category, values in expected.items():
            self.assertEqual(summary.loc[category, pipeline.AMOUNTS].tolist(), values)

    def reject(self, frame, exceptions=(ValueError, TypeError)):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            frame.to_csv(path, index=False)
            with self.assertRaises(exceptions):
                pipeline.load_orders(path)

    def test_16_reject_duplicate_ids(self):
        frame = self.raw.copy()
        frame.loc[1, "order_id"] = frame.loc[0, "order_id"]
        self.reject(frame)

    def test_17_reject_missing_values(self):
        for col in ["category", "order_id"]:
            with self.subTest(column=col):
                frame = self.raw.copy()
                frame.loc[0, col] = None
                self.reject(frame)

    def test_18_reject_invalid_ranges(self):
        for col, value in [("quantity", 0), ("quantity", -1),
                           ("unit_price_toman", -1), ("returned_quantity", -1),
                           ("returned_quantity", 999)]:
            with self.subTest(column=col, value=value):
                frame = self.raw.copy()
                frame.loc[0, col] = value
                self.reject(frame)

    def test_19_reject_unknown_category(self):
        frame = self.raw.copy()
        frame.loc[0, "category"] = "Unknown"
        self.reject(frame)

    def test_20_reject_empty_or_wrong_schema(self):
        self.reject(self.raw.iloc[:0])
        self.reject(self.raw.drop(columns="category"))
        self.reject(self.raw.assign(extra=1))
        self.reject(self.raw[list(reversed(self.raw.columns))])

    def test_21_reject_noninteger_quantity(self):
        frame = self.raw.copy()
        frame["quantity"] = frame["quantity"].astype(str)
        frame.loc[0, "quantity"] = "1.5"
        self.reject(frame)

    def test_22_plot_values_labels_and_zero(self):
        before = self.summary.copy(deep=True)
        fig, ax = pipeline.draw_category_chart(self.summary)
        try:
            np.testing.assert_allclose([p.get_height() for p in ax.patches],
                                       [2.45, 0.69, 0.45], rtol=0, atol=1e-12)
            self.assertEqual([t.get_text() for t in ax.get_xticklabels()],
                             ["Digital", "Books", "Stationery"])
            self.assertEqual(ax.get_ylim()[0], 0)
            self.assertIn("million toman", ax.get_ylabel())
            self.assertNotIn("profit", ax.get_title().lower())
            assert_frame_equal(self.summary, before)
        finally:
            plt.close(fig)

    def test_23_reference_script_from_other_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "chapter-06"
            copy.mkdir()
            shutil.copy(ROOT / "analysis.py", copy)
            shutil.copytree(ROOT / "data", copy / "data")
            before = (copy / "data/orders.csv").read_bytes()
            run = subprocess.run([sys.executable, str(copy / "analysis.py")],
                                 cwd=directory, text=True, capture_output=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("retained_toman=3590000", run.stdout)
            self.assertEqual((copy / "data/orders.csv").read_bytes(), before)
            exported = pd.read_csv(copy / "outputs/category-summary.csv", index_col="category")
            self.assertEqual(int(exported["retained_toman"].sum()), 3590000)
            png = (copy / "outputs/category-retained.png").read_bytes()
            self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertGreater(len(png), 1000)

    def test_24_all_examples_exact_outputs(self):
        # Keep generated outputs away from the released package.
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            shutil.copytree(ROOT / "data", tmp / "data")
            namespace = {}
            cwd = Path.cwd()
            try:
                import os
                os.chdir(tmp)
                for item in CATALOG:
                    with self.subTest(example=item["id"]):
                        capture = io.StringIO()
                        with contextlib.redirect_stdout(capture):
                            exec(compile(item["code"], item["id"], "exec"), namespace)
                        self.assertEqual(capture.getvalue(), item["output"])
            finally:
                os.chdir(cwd)

    def test_25_all_answers_exact_outputs(self):
        for item in ANSWERS:
            with self.subTest(answer=item["id"]):
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture):
                    exec(compile(item["code"], item["id"], "exec"), {})
                self.assertEqual(capture.getvalue(), item["output"])
                text = (ROOT / "chapter-06-full-fa.txt").read_text()
                self.assertIn('```python\n'+item["code"]+'```', text)
                self.assertIn('```text\n'+item["output"]+'```', text)

    def test_26_intentional_error_types(self):
        errors = json.loads((ROOT / "examples/intentional-errors.json").read_text())
        self.assertEqual(len(errors), 6)
        for item in errors:
            with self.subTest(error=item["id"]):
                with self.assertRaises(getattr(builtins, item["exception"])) as caught:
                    exec(item["code"], {})
                self.assertIs(type(caught.exception), getattr(builtins, item["exception"]))

    def test_27_notebook_and_script_match_catalog(self):
        notebook = nbformat.read(ROOT / "notebooks/06-first-end-to-end-analysis.ipynb", as_version=4)
        nbformat.validate(notebook)
        cells = [c for c in notebook.cells if c.cell_type == "code"]
        self.assertEqual(len(cells), 24)
        script = (ROOT / "examples/06-walkthrough.py").read_text()
        text = (ROOT / "chapter-06-full-fa.txt").read_text()
        for cell, item in zip(cells, CATALOG):
            self.assertEqual(cell.source, item["code"].rstrip())
            self.assertEqual(cell.metadata["example_id"], item["id"])
            self.assertEqual(cell.outputs, [])
            self.assertIsNone(cell.execution_count)
            self.assertIn(item["code"], script)
            self.assertIn('```python\n'+item["code"]+'```', text)
            self.assertIn('```text\n'+item["output"]+'```', text)

    def test_28_ascii_code_and_outputs(self):
        for path in ROOT.rglob("*.py"):
            self.assertTrue(path.read_text().isascii(), str(path))
        for item in CATALOG + ANSWERS:
            self.assertTrue(item["code"].isascii(), item["id"])
            self.assertTrue(item["output"].isascii(), item["id"])
        text = (ROOT / "chapter-06-full-fa.txt").read_text()
        for block in re.findall(r"```(?:python|text|bash)\n(.*?)```", text, re.S):
            self.assertTrue(block.isascii())
        for item in json.loads((ROOT / "examples/intentional-errors.json").read_text()):
            self.assertTrue(item["code"].isascii())

    def test_29_text_multiplication_witness(self):
        self.assertEqual("30000" * 2, "3000030000")
        self.assertNotEqual("30000" * 2, 60000)

    def test_30_utf8_and_readme_links(self):
        for extension in ["*.txt", "*.md", "*.json", "*.csv"]:
            for path in ROOT.rglob(extension):
                path.read_text(encoding="utf-8")
        text = (ROOT / "README.md").read_text()
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in target:
                self.assertTrue((ROOT / target).exists(), target)

    def test_31_walkthrough_subprocess(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            shutil.copytree(ROOT / "data", tmp / "data")
            run = subprocess.run([sys.executable, str(ROOT / "examples/06-walkthrough.py")],
                                 cwd=tmp, text=True, capture_output=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout, ''.join(item["output"] for item in CATALOG))

    def test_32_answers_subprocess(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run([sys.executable, str(ROOT / "answers/06-solutions.py")],
                                 cwd=directory, text=True, capture_output=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout, ''.join(item["output"] for item in ANSWERS))

    def test_33_released_csv_matches_reference(self):
        exported = pd.read_csv(ROOT / "outputs/category-summary.csv", index_col="category")
        assert_frame_equal(exported[pipeline.AMOUNTS], self.summary[pipeline.AMOUNTS])
        np.testing.assert_allclose(exported["retained_share_pct"],
                                   self.summary["retained_share_pct"], rtol=0, atol=0.00000051)

    def test_34_contract_limit_date_not_validated(self):
        # Record the limit instead of implying full date validation.
        frame = self.raw.copy()
        frame.loc[0, "order_date"] = "not-a-date"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "date.csv"
            frame.to_csv(path, index=False)
            self.assertEqual(pipeline.load_orders(path).loc[0, "order_date"], "not-a-date")


if __name__ == "__main__":
    unittest.main()
