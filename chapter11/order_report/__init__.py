"""Educational order reporting with explicit failure contracts."""
from .errors import DataContractError, ReportInvariantError
from .service import run_report
__all__ = ["DataContractError", "ReportInvariantError", "run_report"]
