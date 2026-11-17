"""Run from any working directory; output path is anchored to this file."""
import json
from pathlib import Path
from analysis import build_report
from data.sample_orders import orders

ROOT = Path(__file__).resolve().parent
report = build_report(orders)
output = ROOT / "outputs/report.json"
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
print("orders", report["order_count"])
print("retained_toman", report["retained_toman"])
for group in report["groups"]:
    print(group["category"], group["retained_toman"])
