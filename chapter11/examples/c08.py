try:
    raise FileNotFoundError("missing input")
except FileNotFoundError:
    print("missing file")
except OSError:
    print("other io failure")
