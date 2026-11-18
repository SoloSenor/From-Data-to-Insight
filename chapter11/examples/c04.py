import traceback

def divide(total, count):
    return total / count

def report():
    return divide(100, 0)

try:
    report()
except ZeroDivisionError as exc:
    frames = traceback.extract_tb(exc.__traceback__)
    print([frame.name for frame in frames[-2:]])
    print(type(exc).__name__)
