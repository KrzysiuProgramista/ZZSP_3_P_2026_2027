import numpy as np
import pandas as pd

# 1) Series from a list of 6 numbers (default RangeIndex per notes)
s_default = pd.Series([10, 20, 30, 40, 50, 60])
print("Default Series:")
print(s_default)
print("Index:", s_default.index)
print()

# 2) Series with a custom string index
s = pd.Series([10, 20, 30, 40, 50, 60], index=["a", "b", "c", "d", "e", "f"])
print("Custom-index Series:")
print(s)
print()

# 3) Series from a dictionary — by analogy with the DataFrame-from-dict note
#    ("keys become the column labels"), for a Series the dict keys become the index.
s_from_dict = pd.Series({"a": 10, "b": 20, "c": 30, "d": 40, "e": 50, "f": 60})
print("Series from dict:")
print(s_from_dict)
print("Index (keys became the index):", s_from_dict.index)
print()

# 4) Access by label vs by position
print('s["a"] (by label):', s["a"])
print("s.iloc[0] (by position):", s.iloc[0])
print()

# 5) Attributes
print("s.values:", s.values)
print("s.index :", s.index)
print("s.dtype :", s.dtype)
print("s.name  :", s.name)
print()

# 6) Arithmetic on the whole Series
print("s * 2:")
print(s * 2)
print()
print("s + 10:")
print(s + 10)
print()
print("s > 15:")
print(s > 15)


# used about 0.6$ (most of it was probably the amount of credits used to
# read the md file and add it to context)