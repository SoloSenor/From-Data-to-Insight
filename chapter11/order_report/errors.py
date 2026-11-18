"""Domain exceptions without raw input values in public messages."""
class DataContractError(ValueError):
    """Signal an expected violation of the educational input contract."""
    def __init__(self, code, record_number=None, field=None):
        self.code = code
        self.record_number = record_number
        self.field = field
        parts = [code]
        if record_number is not None:
            parts.append(f"record={record_number}")
        if field is not None:
            parts.append(f"field={field}")
        super().__init__(" ".join(parts))


class ReportInvariantError(RuntimeError):
    """Signal an unexpected inconsistency in a generated report."""
