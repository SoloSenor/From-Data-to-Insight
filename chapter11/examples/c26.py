import math
value = 1e-10
print(math.isclose(value, 0.0, rel_tol=1e-6))
print(math.isclose(value, 0.0, rel_tol=1e-6, abs_tol=1e-9))
