"""Check the minimum environment used in chapter 2; no external data required."""

from importlib.util import find_spec
from importlib import metadata
from pathlib import Path
import sys


def main():
    print("Python:", sys.version.split()[0])
    print("Executable:", sys.executable)
    print("Working directory:", Path.cwd())
    in_venv = sys.prefix != sys.base_prefix
    print("Virtual environment:", in_venv)

    problems = []
    if not in_venv:
        problems.append("Interpreter is not running inside a standard venv.")

    for package in ("jupyterlab", "ipykernel"):
        try:
            if find_spec(package) is None:
                problems.append(f"{package}: module is not discoverable.")
            else:
                print(f"{package}: {metadata.version(package)}")
        except (ImportError, metadata.PackageNotFoundError) as exc:
            problems.append(f"{package}: {exc}")

    orders = 2700
    working_days = 27
    orders_per_day = orders / working_days
    assert orders_per_day == 100.0
    print("Orders per working day:", orders_per_day)

    if problems:
        print("Environment needs attention:")
        for problem in problems:
            print("-", problem)
        return 1

    print("Package discovery is not a Jupyter server or kernel startup test.")
    print("Minimum chapter checks passed; this is not a complete project validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
