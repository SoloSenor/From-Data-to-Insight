from collections import Counter
categories = ["Books", "Digital", "Books", "Stationery"]
counts = Counter(categories)
print(sorted(counts.items()))
print(counts["Missing"])
print("Missing" in counts)
