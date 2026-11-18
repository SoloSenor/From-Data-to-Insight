"""Run coding answers from the chapter root in fresh processes."""
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
def main():
    items = json.loads((ROOT / "examples/problems.json").read_text(encoding="utf-8"))
    for item in items:
        if "code" not in item:
            continue
        result = subprocess.run([sys.executable, "-c", item["code"]], cwd=ROOT,
                                capture_output=True, text=True, check=True)
        if result.stdout != item["output"] or result.stderr:
            raise RuntimeError(f"Mismatch: {item['id']}")
        print(item["id"], "PASS")
if __name__ == "__main__":
    main()
