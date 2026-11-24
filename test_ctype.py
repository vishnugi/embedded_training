import ctypes
from pathlib import Path

library_path = Path(_file_).parent / "libmathlib.so"
mathlib = ctypes.CDLL(str(library_path))

# Describe the C function to Python.
mathlib.add.argtypes = [ctypes.c_int, ctypes.c_int]
mathlib.add.restype = ctypes.c_int

result = mathlib.add(10, 20)

print("ctypes result:", result)
