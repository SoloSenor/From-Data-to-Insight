import subprocess
import sys

code = "assert False, 'blocked'; print('continued')"
normal = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
optimized = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True)
print(normal.returncode != 0)
print(optimized.returncode)
print(optimized.stdout.strip())
