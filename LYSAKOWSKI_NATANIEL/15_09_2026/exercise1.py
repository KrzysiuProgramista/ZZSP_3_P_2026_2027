import numpy as np
import pandas as pd

# 1. Series from a list of 6 numbers - default integer index
s = pd.Series([1, 3, 5, np.nan, 6, 8])
print(s)
print("index:", s.index.tolist())

# 2. Series with a custom string index
s2 = pd.Series([1, 3, 5, np.nan, 6, 8], index=["a", "b", "c", "d", "e", "f"])
print(s2)

# 3. Series from a dictionary - keys become the index
s3 = pd.Series({"a": 1, "b": 2, "c": 3})
print(s3)
print("index:", s3.index.tolist())

# 4. Access an element by label and by position
print("by label:   ", s2["b"])
print("by position:", s2.iloc[0])

# 5. Inspect the underlying data and metadata
print("values:", s.values)
print("index:", s.index)
print("dtype:", s.dtype)
print("name:", s.name)

# 6. Arithmetic on the whole Series (aligns by index)
print("s * 2:\n", s * 2)
print("s + 10:\n", s + 10)
print("s > 15:\n", s > 15)
