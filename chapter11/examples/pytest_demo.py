"""Optional: python -m pytest -q examples/pytest_demo.py."""
import pytest
from order_report.errors import DataContractError
from order_report.validation import validate_order

@pytest.mark.parametrize("returned, expected", [(0, 300), (1, 200), (3, 0)])
def test_retained_cases(returned, expected):
    assert (3 - returned) * 100 == expected

def test_invalid_quantity():
    row = dict(order_id="A", order_date="2024-01-01", category="Books",
               quantity=0, unit_price_toman=100, returned_quantity=0)
    with pytest.raises(DataContractError, match="positive_quantity_required"):
        validate_order(row)
