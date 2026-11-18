"""Own the generator and return a report only after complete success."""
from contextlib import closing
from .source import iter_orders_csv
from .pipeline import summarize_orders


def run_report(path):
    with closing(iter_orders_csv(path)) as rows:
        return summarize_orders(rows)
