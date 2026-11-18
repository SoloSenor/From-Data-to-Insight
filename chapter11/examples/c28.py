def read_and_total(reader):
    return sum(reader())

def failed_reader():
    raise OSError("simulated read failure")

try:
    read_and_total(failed_reader)
except OSError:
    print("io failure propagated")
