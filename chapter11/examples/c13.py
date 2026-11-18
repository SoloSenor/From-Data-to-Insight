class DataContractError(ValueError):
    pass

def parse_quantity(text):
    try:
        return int(text)
    except ValueError as exc:
        raise DataContractError("invalid_integer record=2 field=quantity") from exc

try:
    parse_quantity("bad")
except DataContractError as exc:
    print(str(exc))
    print(type(exc.__cause__).__name__)
