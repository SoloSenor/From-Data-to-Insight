from datetime import date, timedelta
start = date.fromisoformat("2024-02-28")
end = date.fromisoformat("2024-03-01")
print((end - start).days)
print((start + timedelta(days=2)).isoformat())
