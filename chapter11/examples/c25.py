import math
for value in (1.5, float("nan"), float("inf")):
    print(math.isfinite(value))
print(float("nan") == float("nan"))
