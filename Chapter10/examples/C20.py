from collections import defaultdict
totals = defaultdict(int)
print(totals.get("Books"))
print("Books" in totals)
print(totals["Books"])
print("Books" in totals)
totals["Books"] += 120
print(dict(totals))
