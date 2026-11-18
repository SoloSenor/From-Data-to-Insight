events = []
def middle():
    try:
        int("bad")
    except ValueError:
        events.append("observed")
        raise

try:
    middle()
except ValueError:
    print(events)
    print("still failed")
