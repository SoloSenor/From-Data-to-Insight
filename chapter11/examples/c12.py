class DataContractError(ValueError):
    pass

try:
    raise DataContractError("invalid_quantity record=2")
except DataContractError as exc:
    print(type(exc).__name__)
    print(str(exc))
