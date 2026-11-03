import pandas as pd

s1 = pd.Series([10, 20, 5, 30, 15, 25])
print(s1)
print(s1.index)

s2 = pd.Series([10, 20, 5, 30, 15, 25], index=["a", "b", "c", "d", "e", "f"], name="values")
print(s2)

s3 = pd.Series({"Warsaw": 1_860_000, "Krakow": 800_000, "Lodz": 655_000})
print(s3)
print(s3.index)

print(s2["a"])
print(s2.iloc[0])

print(s2.values)
print(s2.index)
print(s2.dtype)
print(s2.name)

print(s2 * 2)
print(s2 + 10)
print(s2 > 15)