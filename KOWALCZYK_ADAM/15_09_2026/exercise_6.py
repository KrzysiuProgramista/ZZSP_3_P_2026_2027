import numpy as np
import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(data)

subjects = ["maths", "physics", "english"]

# 1) average — mean across the three subject columns (axis=1 -> per row).
df_grades["average"] = df_grades[subjects].mean(axis=1)

# 2) passed — element-wise comparison on a Series returns a boolean Series.
df_grades["passed"] = df_grades["average"] >= 3.0

# 3) best_subject — idxmax returns the *label* of the max; with axis=1 that label
#    is the column name, i.e. the subject with the highest grade in that row.
#    (Ties go to the leftmost column in `subjects`.)
df_grades["best_subject"] = df_grades[subjects].idxmax(axis=1)

# 4) sort_values sorts by the actual values; ascending=False -> highest first.
print(df_grades.sort_values(by="average", ascending=False))

# used 0.20$