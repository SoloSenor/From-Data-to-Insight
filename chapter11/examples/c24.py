import math
value = 0.1 + 0.2
print(value == 0.3)
print(math.isclose(value, 0.3, rel_tol=1e-12, abs_tol=1e-12))
