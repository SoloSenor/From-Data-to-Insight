"""Executable contracts, independent oracles and failure-path tests."""
import copy
import csv
import io
import json
import math
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from order_report.errors import DataContractError, ReportInvariantError
from order_report.validation import validate_order, FIELDS
from order_report.source import iter_orders_csv
from order_report.pipeline import ReportAccumulator, summarize_orders, check_report, format_report
from order_report.service import run_report
from order_report.cli import main


def row(**changes):
    result = dict(order_id="A", order_date="2024-01-01", category="Books",
                  quantity=3, unit_price_toman=100, returned_quantity=1)
    result.update(changes)
    return result


def csv_text(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


class CatalogTests(unittest.TestCase):
    pass


def add_program_test(name, code, expected, error=None):
    def test(self):
        self.assertTrue(code.isascii())
        result = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                                capture_output=True, text=True, timeout=45)
        if error:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(error, result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.stderr, "")
            self.assertTrue(result.stdout.isascii())
    setattr(CatalogTests, name, test)

for item in json.loads((ROOT / "examples/catalog.json").read_text(encoding="utf-8")):
    add_program_test("test_example_" + item["id"], item["code"], item["output"])
for item in json.loads((ROOT / "examples/problems.json").read_text(encoding="utf-8")):
    if "code" in item:
        add_program_test("test_answer_" + item["id"], item["code"], item["output"])
for item in json.loads((ROOT / "examples/intentional-errors.json").read_text(encoding="utf-8")):
    add_program_test("test_broken_" + item["id"], item["broken_code"],
                     item["broken_output"], item["exception"])
    add_program_test("test_fixed_" + item["id"], item["fixed_code"], item["fixed_output"])


class ValidationTests(unittest.TestCase):
    def test_valid_and_unchanged(self):
        source = row()
        before = copy.deepcopy(source)
        self.assertIsNone(validate_order(source))
        self.assertEqual(source, before)

    def test_invalid_date_cause(self):
        with self.assertRaises(DataContractError) as caught:
            validate_order(row(order_date="2024-02-30"), 4)
        self.assertEqual(caught.exception.code, "invalid_date")
        self.assertEqual(caught.exception.record_number, 4)
        self.assertEqual(caught.exception.field, "order_date")
        self.assertIsInstance(caught.exception.__cause__, ValueError)

    def test_noncanonical_date(self):
        with self.assertRaisesRegex(DataContractError, "canonical_date_required"):
            validate_order(row(order_date="20240101"))

    def test_missing_field(self):
        source = row(); del source["quantity"]
        with self.assertRaisesRegex(DataContractError, "unexpected_fields"):
            validate_order(source)

    def test_extra_field(self):
        with self.assertRaisesRegex(DataContractError, "unexpected_fields"):
            validate_order(row(extra=1))

    def test_nondict(self):
        with self.assertRaises(DataContractError):
            validate_order([])

    def test_leap_date(self):
        self.assertIsNone(validate_order(row(order_date="2024-02-29")))

    def test_zero_price_allowed(self):
        self.assertIsNone(validate_order(row(unit_price_toman=0)))

    def test_full_return_allowed(self):
        self.assertIsNone(validate_order(row(returned_quantity=3)))

invalid_cases = [
    ("zero_quantity", "quantity", 0, "positive_quantity_required"),
    ("negative_quantity", "quantity", -1, "positive_quantity_required"),
    ("float_quantity", "quantity", 3.0, "integer_required"),
    ("bool_quantity", "quantity", True, "integer_required"),
    ("text_quantity", "quantity", "3", "integer_required"),
    ("negative_price", "unit_price_toman", -1, "nonnegative_price_required"),
    ("float_price", "unit_price_toman", 1.0, "integer_required"),
    ("bool_price", "unit_price_toman", True, "integer_required"),
    ("negative_return", "returned_quantity", -1, "invalid_returned_quantity"),
    ("excess_return", "returned_quantity", 4, "invalid_returned_quantity"),
    ("bool_return", "returned_quantity", False, "integer_required"),
    ("none_id", "order_id", None, "nonblank_text_required"),
    ("blank_id", "order_id", "", "nonblank_text_required"),
    ("id_whitespace", "order_id", " A ", "outer_whitespace"),
    ("blank_category", "category", "  ", "nonblank_text_required"),
    ("category_whitespace", "category", "Books ", "outer_whitespace"),
]
for name, field, value, expected in invalid_cases:
    def test(self, field=field, value=value, expected=expected):
        with self.assertRaises(DataContractError) as caught:
            validate_order(row(**{field: value}), 9)
        self.assertEqual(caught.exception.code, expected)
        self.assertEqual(caught.exception.field, field)
        self.assertEqual(caught.exception.record_number, 9)
    setattr(ValidationTests, "test_" + name, test)


class PipelineTests(unittest.TestCase):
    def test_manual_oracle(self):
        report = summarize_orders([row(), row(order_id="B", quantity=2,
                                   unit_price_toman=50, returned_quantity=0)])
        self.assertEqual(tuple(report[k] for k in
             ("orders", "gross_toman", "refund_toman", "retained_toman")), (2,400,100,300))

    def test_reference_totals(self):
        report = run_report(ROOT / "data/orders.csv")
        self.assertEqual(report["orders"],12)
        self.assertEqual(report["gross_toman"],5020000)
        self.assertEqual(report["refund_toman"],1430000)
        self.assertEqual(report["retained_toman"],3590000)
        self.assertEqual({r["category"]:r["retained_toman"] for r in report["categories"]},
                         {"Digital":2450000,"Books":690000,"Stationery":450000})

    def test_reference_records_match_json(self):
        rows = list(iter_orders_csv(ROOT / "data/orders.csv"))
        expected = json.loads((ROOT / "data/orders.json").read_text())
        self.assertEqual(rows, expected)

    def test_empty_report(self):
        self.assertEqual(summarize_orders([]), dict(orders=0,gross_toman=0,
                         refund_toman=0,retained_toman=0,categories=[]))

    def test_all_returned_share_undefined(self):
        report = summarize_orders([row(returned_quantity=3)])
        self.assertEqual(report["retained_toman"],0)
        self.assertIsNone(report["categories"][0]["share"])
        self.assertIn("NA",format_report(report))

    def test_price_zero(self):
        report = summarize_orders([row(unit_price_toman=0)])
        self.assertEqual(report["gross_toman"],0)
        self.assertIsNone(report["categories"][0]["share"])

    def test_no_return(self):
        report=summarize_orders([row(returned_quantity=0)])
        self.assertEqual(report["retained_toman"],300)

    def test_duplicate(self):
        with self.assertRaises(DataContractError) as caught:
            summarize_orders([row(),row()])
        self.assertEqual(caught.exception.code,"duplicate_order_id")
        self.assertEqual(caught.exception.record_number,2)

    def test_bad_record_does_not_mutate_accumulator(self):
        acc=ReportAccumulator(); acc.add(row())
        before=acc.snapshot()
        with self.assertRaises(DataContractError):
            acc.add(row(order_id="B",returned_quantity=4))
        self.assertEqual(acc.snapshot(),before)
        acc.add(row(order_id="B"))
        self.assertEqual(acc.snapshot()["orders"],2)

    def test_duplicate_does_not_mutate_accumulator(self):
        acc=ReportAccumulator(); acc.add(row()); before=acc.snapshot()
        with self.assertRaises(DataContractError):acc.add(row())
        self.assertEqual(acc.snapshot(),before)

    def test_snapshot_independent(self):
        acc=ReportAccumulator();acc.add(row())
        report=acc.snapshot();report["categories"][0]["retained_toman"]=-10
        self.assertEqual(acc.snapshot()["categories"][0]["retained_toman"],200)

    def test_instance_independent(self):
        a,b=ReportAccumulator(),ReportAccumulator();a.add(row())
        self.assertEqual(b.snapshot()["orders"],0)

    def test_input_not_mutated(self):
        rows=[row(),row(order_id="B")]; before=copy.deepcopy(rows)
        summarize_orders(rows)
        self.assertEqual(rows,before)

    def test_single_pass(self):
        class Once:
            def __init__(self):self.iterations=0
            def __iter__(self):
                self.iterations+=1
                if self.iterations>1:raise RuntimeError("second traversal")
                yield row()
        source=Once()
        self.assertEqual(summarize_orders(source)["orders"],1)
        self.assertEqual(source.iterations,1)

    def test_order_invariance(self):
        rows=[row(),row(order_id="B",category="Digital")]
        self.assertEqual(summarize_orders(rows),summarize_orders(reversed(rows)))

    def test_price_scaling(self):
        rows=[row(),row(order_id="B")]
        scaled=[dict(r,unit_price_toman=r["unit_price_toman"]*2) for r in rows]
        self.assertEqual(summarize_orders(scaled)["retained_toman"],
                         2*summarize_orders(rows)["retained_toman"])

    def test_tie_break_deterministic(self):
        report=summarize_orders([row(category="Z"),row(order_id="B",category="A")])
        self.assertEqual([r["category"] for r in report["categories"]],["A","Z"])

    def test_generator_failure_propagates(self):
        def failing():
            yield row()
            raise RuntimeError("broken producer")
        with self.assertRaisesRegex(RuntimeError,"broken producer"):
            summarize_orders(failing())

    def test_service_owns_closure_after_failure(self):
        events=[]
        def source():
            try:
                yield row(quantity=0)
            finally:
                events.append("closed")
        with patch("order_report.service.iter_orders_csv",return_value=source()):
            with self.assertRaises(DataContractError):run_report("unused.csv")
        self.assertEqual(events,["closed"])

    def test_reference_output(self):
        actual=format_report(run_report(ROOT/"data/orders.csv"))+"\n"
        self.assertEqual(actual,(ROOT/"outputs/report.txt").read_text())


class InvariantTests(unittest.TestCase):
    def test_total_balance(self):
        report=summarize_orders([row()]);report["retained_toman"]=299
        with self.assertRaisesRegex(ReportInvariantError,"total_balance"):
            check_report(report)
    def test_category_balance(self):
        report=summarize_orders([row()]);report["categories"][0]["retained_toman"]=199
        with self.assertRaisesRegex(ReportInvariantError,"category_balance"):
            check_report(report)
    def test_negative_total(self):
        report=summarize_orders([]);report["orders"]=-1
        with self.assertRaisesRegex(ReportInvariantError,"nonnegative"):
            check_report(report)
    def test_boolean_total(self):
        report=summarize_orders([]);report["orders"]=True
        with self.assertRaises(ReportInvariantError):check_report(report)
    def test_undefined_share(self):
        report=summarize_orders([row(unit_price_toman=0)])
        report["categories"][0]["share"]=0.0
        with self.assertRaisesRegex(ReportInvariantError,"undefined_share"):
            check_report(report)
    def test_wrong_shares_still_sum_one(self):
        report=summarize_orders([row(category="A"),row(order_id="B",category="B",unit_price_toman=50)])
        report["categories"][0]["share"]=0.5
        report["categories"][1]["share"]=0.5
        with self.assertRaisesRegex(ReportInvariantError,"invalid_category_share"):
            check_report(report)
    def test_correct_share_rounding(self):
        report=summarize_orders([row(category="A"),row(order_id="B",category="B",unit_price_toman=50)])
        self.assertIsNone(check_report(report))

for name,value in [("nan",float("nan")),("inf",float("inf")),("negative",-0.1),
                   ("over_one",1.1),("bool",True),("none",None),("text","1")]:
    def test(self,value=value):
        report=summarize_orders([row()]);report["categories"][0]["share"]=value
        with self.assertRaisesRegex(ReportInvariantError,"invalid_category_share"):
            check_report(report)
    setattr(InvariantTests,"test_share_"+name,test)


class SourceTests(unittest.TestCase):
    def setUp(self):
        directory=TemporaryDirectory();self.addCleanup(directory.cleanup)
        self.path=Path(directory.name)/"input.csv"
    def write(self,text,encoding="utf-8"):
        self.path.write_text(text,encoding=encoding)
    def test_real_roundtrip(self):
        self.write(csv_text([row()]))
        self.assertEqual(list(iter_orders_csv(self.path)),[row()])
    def test_header_only(self):
        self.write(csv_text([]))
        self.assertEqual(list(iter_orders_csv(self.path)),[])
    def test_empty_file_invalid(self):
        self.write("")
        with self.assertRaisesRegex(DataContractError,"invalid_header"):
            list(iter_orders_csv(self.path))
    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):list(iter_orders_csv(self.path))
    def test_wrong_header(self):
        self.write("id,price\nA,2\n")
        with self.assertRaisesRegex(DataContractError,"invalid_header"):
            list(iter_orders_csv(self.path))
    def test_bom(self):
        self.write(csv_text([row()]),"utf-8-sig")
        self.assertEqual(list(iter_orders_csv(self.path)),[row()])
    def test_quoted_comma(self):
        self.write(csv_text([row(category="Books,Special")]))
        self.assertEqual(list(iter_orders_csv(self.path))[0]["category"],"Books,Special")
    def test_logical_not_physical_record_number(self):
        self.write(csv_text([row(category="Books\nSpecial"),row(order_id="B",quantity=0)]))
        with self.assertRaises(DataContractError) as caught:run_report(self.path)
        self.assertEqual(caught.exception.record_number,2)
    def test_wrong_field_count(self):
        self.write(csv_text([])+"A,2024-01-01,Books,3,100,1,extra\n")
        with self.assertRaisesRegex(DataContractError,"wrong_field_count"):
            list(iter_orders_csv(self.path))
    def test_missing_field_value(self):
        self.write(csv_text([])+"A,2024-01-01,Books,3,100\n")
        with self.assertRaisesRegex(DataContractError,"wrong_field_count"):
            list(iter_orders_csv(self.path))
    def test_bad_integer_context_and_cause(self):
        self.write(csv_text([row(quantity="secret-value")]))
        with self.assertRaises(DataContractError) as caught:list(iter_orders_csv(self.path))
        self.assertEqual(caught.exception.code,"invalid_integer")
        self.assertEqual(caught.exception.record_number,1)
        self.assertEqual(caught.exception.field,"quantity")
        self.assertNotIn("secret-value",str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__,ValueError)
    def test_invalid_encoding(self):
        self.path.write_bytes(b"\xff\xfe")
        with self.assertRaises(DataContractError) as caught:list(iter_orders_csv(self.path))
        self.assertEqual(caught.exception.code,"invalid_encoding")
        self.assertIsInstance(caught.exception.__cause__,UnicodeError)
    def test_invalid_csv(self):
        self.write(csv_text([])+'A,2024-01-01,"unterminated')
        with self.assertRaises(DataContractError) as caught:list(iter_orders_csv(self.path))
        self.assertEqual(caught.exception.code,"invalid_csv")
        self.assertIsInstance(caught.exception.__cause__,csv.Error)
    def test_lazy_open(self):
        with patch("order_report.source.Path.open") as opened:
            rows=iter_orders_csv(self.path)
            opened.assert_not_called()
            rows.close()
            opened.assert_not_called()
    def test_open_handle_closed_after_early_stop(self):
        handle=io.StringIO(csv_text([row(),row(order_id="B")]))
        with patch("order_report.source.Path.open",return_value=handle):
            rows=iter_orders_csv(self.path);next(rows)
            self.assertFalse(handle.closed)
            rows.close()
            self.assertTrue(handle.closed)
    def test_open_handle_closed_on_parse_failure(self):
        handle=io.StringIO(csv_text([row(quantity="bad")]))
        with patch("order_report.source.Path.open",return_value=handle):
            with self.assertRaises(DataContractError):list(iter_orders_csv(self.path))
            self.assertTrue(handle.closed)
    def test_open_handle_closed_on_domain_failure(self):
        handle=io.StringIO(csv_text([row(quantity=0)]))
        with patch("order_report.source.Path.open",return_value=handle):
            with self.assertRaises(DataContractError):run_report(self.path)
            self.assertTrue(handle.closed)
    def test_bad_later_record_returns_no_report(self):
        self.write(csv_text([row(),row(order_id="B",quantity=0)]))
        with self.assertRaises(DataContractError):run_report(self.path)
    def test_parser_does_not_validate_domain(self):
        self.write(csv_text([row(quantity=0)]))
        self.assertEqual(list(iter_orders_csv(self.path))[0]["quantity"],0)
        with self.assertRaises(DataContractError):run_report(self.path)


class CliTests(unittest.TestCase):
    def test_success(self):
        out,err=io.StringIO(),io.StringIO()
        self.assertEqual(main([],out,err),0)
        self.assertEqual(out.getvalue(),(ROOT/"outputs/report.txt").read_text())
        self.assertEqual(err.getvalue(),"")
    def test_missing_file(self):
        out,err=io.StringIO(),io.StringIO()
        with TemporaryDirectory() as directory:
            self.assertEqual(main([str(Path(directory)/"missing")],out,err),2)
        self.assertEqual(out.getvalue(),"")
        self.assertEqual(err.getvalue(),"ERROR io: cannot read input file\n")
    def test_bad_later_record_stdout_empty(self):
        out,err=io.StringIO(),io.StringIO()
        with TemporaryDirectory() as directory:
            path=Path(directory)/"bad.csv";path.write_text(csv_text([row(),row(order_id="B",quantity=0)]))
            self.assertEqual(main([str(path)],out,err),3)
        self.assertEqual(out.getvalue(),"")
        self.assertIn("record=2",err.getvalue())
    def test_raw_value_not_in_public_error(self):
        out,err=io.StringIO(),io.StringIO()
        with TemporaryDirectory() as directory:
            path=Path(directory)/"private.csv";path.write_text(csv_text([row(quantity="SECRET_TOKEN")]))
            self.assertEqual(main([str(path)],out,err),3)
        self.assertNotIn("SECRET_TOKEN",err.getvalue())
        self.assertNotIn("private.csv",err.getvalue())
    def test_unexpected_bug_propagates(self):
        with patch("order_report.cli.run_report",side_effect=KeyError("bug")):
            with self.assertRaises(KeyError):main([],io.StringIO(),io.StringIO())
    def test_invariant_error_not_mislabeled(self):
        with patch("order_report.cli.run_report",side_effect=ReportInvariantError("bug")):
            with self.assertRaises(ReportInvariantError):main([],io.StringIO(),io.StringIO())
    def test_keyboard_interrupt_not_swallowed(self):
        with patch("order_report.cli.run_report",side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):main([],io.StringIO(),io.StringIO())
    def test_debug_reraises_known_error(self):
        exc=DataContractError("simulated")
        with patch("order_report.cli.run_report",side_effect=exc):
            with self.assertRaises(DataContractError) as caught:main(["--debug"],io.StringIO(),io.StringIO())
        self.assertIs(caught.exception,exc)
    def test_permission_error(self):
        out,err=io.StringIO(),io.StringIO()
        with patch("order_report.cli.run_report",side_effect=PermissionError("secret path")):
            self.assertEqual(main([],out,err),2)
        self.assertNotIn("secret",err.getvalue())
    def test_module_process(self):
        result=subprocess.run([sys.executable,"-m","order_report"],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,(ROOT/"outputs/report.txt").read_text())
    def test_script_from_other_working_directory(self):
        with TemporaryDirectory() as directory:
            result=subprocess.run([sys.executable,str(ROOT/"run_analysis.py")],cwd=directory,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,(ROOT/"outputs/report.txt").read_text())
    def test_optimized_validation_still_rejects(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/"bad.csv";path.write_text(csv_text([row(quantity=0)]))
            result=subprocess.run([sys.executable,"-O","-m","order_report",str(path)],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,3,result.stderr)
        self.assertEqual(result.stdout,"")
        self.assertIn("positive_quantity_required",result.stderr)
    def test_import_has_no_output(self):
        result=subprocess.run([sys.executable,"-c","import order_report"],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual((result.returncode,result.stdout,result.stderr),(0,"",""))


class EditorialTests(unittest.TestCase):
    def test_all_python_files_ascii_and_compile(self):
        for path in ROOT.rglob("*.py"):
            with self.subTest(file=path.name):
                text=path.read_text();self.assertTrue(text.isascii())
                compile(text,str(path),"exec")
    def test_catalog_count(self):
        self.assertEqual(len(json.loads((ROOT/"examples/catalog.json").read_text())),30)
    def test_problem_count(self):
        self.assertEqual(len(json.loads((ROOT/"examples/problems.json").read_text())),12)
    def test_trap_count(self):
        self.assertEqual(len(json.loads((ROOT/"examples/intentional-errors.json").read_text())),8)

if __name__ == "__main__":
    unittest.main()
