import numpy as np
import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(data)

# head / tail / sample
print("df.head(2):")
print(df_grades.head(2))
print()

print("df.tail(2):")
print(df_grades.tail(2))
print()

# sample(3) picks 3 random rows (not covered in the md, standard pandas).
print("df.sample(3):")
print(df_grades.sample(3))
print()

# One label vs. list-of-labels — see md "With []":
#   df["A"]        # one label -> the column as a Series
#   df[["B", "A"]] # list of labels -> subset (a DataFrame with those columns)
single = df_grades["maths"]
multi  = df_grades[["maths", "physics"]]

print('type(df["maths"]):        ', type(single).__name__)
print('type(df[["maths","physics"]]):', type(multi).__name__)
print()

# Difference:
#   df["maths"]                is a 1D Series  — one column pulled out with its index.
#   df[["maths", "physics"]]   is a 2D DataFrame — a subset of columns, still a table.
# Rule of thumb: a single label gives you a Series, a list of labels gives you a DataFrame,
# even if that list has just one item (df[["maths"]] is still a DataFrame).

# Reductions on the "maths" Series.
m = df_grades["maths"]
print("maths.mean():", m.mean())
print("maths.max() :", m.max())
print("maths.min() :", m.min())
print("maths.sum() :", m.sum())
print("maths.std() :", m.std())
print()

# The same reduction across every column at once.
# numeric_only=True skips non-numeric columns (here: "student").
print("df.mean(numeric_only=True):")
print(df_grades.mean(numeric_only=True))


# used 0.17$