import numpy as np
import pandas as pd

# 1. Create a Series from a list of 6 numbers. Print it. Note the index.
s = pd.Series([1, 2, 3, 4, 5, 6])
print(s)
print("index:", s.index.tolist())
print()

# 2. Create one with a custom string index.
s = pd.Series([1, 2, 3, 4, 5, 6], index=["a", "b", "c", "d", "e", "f"])
print(s)
print()

# 3. Create one from a dictionary - what becomes the index?
s = pd.Series({"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6})
print(s)
print("index:", s.index.tolist())
print()

# 4. Access an element by label and by position (s["a"] vs s.iloc[0]).
print("by label  s['a'] =", s["a"])
print("by pos    s.iloc[0] =", s.iloc[0])
print()

# 5. Print s.values, s.index, s.dtype, s.name.
print("values:", s.values)
print("index:", s.index.tolist())
print("dtype:", s.dtype)
print("name:", s.name)
print()

# 6. Do arithmetic on the whole Series: s * 2, s + 10, s > 15.
print("s * 2:")
print(s * 2)
print()
print("s + 10:")
print(s + 10)
print()
print("s > 15:")
print(s > 15)
