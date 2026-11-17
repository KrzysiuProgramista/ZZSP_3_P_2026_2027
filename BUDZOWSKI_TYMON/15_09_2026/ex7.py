import pandas as pd

a = pd.Series([10, 20, 30], index=["x", "y", "z"])
b = pd.Series([1, 2, 3], index=["y", "z", "w"])

print(a + b)

print(a.add(b, fill_value=0))

# The index is what makes pandas different from a list of lists: every value carries a label,
# and operations match values by label, not by position. a + b pairs "y" with "y" and "z" with "z"
# no matter where they sit, while a list of lists would blindly combine element 0 with element 0.
# The index also gives you label lookup (s["y"]), automatic alignment when adding columns
# or merging, and makes missing matches visible as NaN instead of silently producing wrong numbers.