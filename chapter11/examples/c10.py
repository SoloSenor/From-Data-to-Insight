events = []
try:
    try:
        events.append("start")
        raise ValueError("invalid input")
    finally:
        events.append("cleanup")
except ValueError:
    events.append("handled")
print(events)
