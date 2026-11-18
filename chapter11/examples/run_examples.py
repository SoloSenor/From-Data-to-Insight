"""Execute each independent example in a fresh interpreter."""
import json
from pathlib import Path
import subprocess
import sys

def main():
    catalog = json.loads(Path(__file__).with_name("catalog.json").read_text(encoding="utf-8"))
    for item in catalog:
        result = subprocess.run([sys.executable, "-c", item["code"]],
                                capture_output=True, text=True, check=True)
        if result.stdout != item["output"] or result.stderr:
            raise RuntimeError(f"Output mismatch: {item['id']}")
        print(item["id"], "PASS")

if __name__ == "__main__":
    main()
