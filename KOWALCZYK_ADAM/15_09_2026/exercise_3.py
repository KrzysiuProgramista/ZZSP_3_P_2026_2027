import numpy as np
import pandas as pd

# 1) From a list of dictionaries (one dict per row).
#    Each dict's keys become the column labels; missing keys would become NaN.
rows = [
    {"student": "Anna",  "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola",   "maths": 4, "physics": 5, "english": 4},
    {"student": "Marek", "maths": 2, "physics": 3, "english": 4},
    {"student": "Kasia", "maths": 5, "physics": 4, "english": 5},
]
df_from_dicts = pd.DataFrame(rows)
print("From list of dicts:")
print(df_from_dicts)
print()

# 2) From a list of lists, passing columns=[...].
#    Same shape as the md's NumPy-array constructor; the outer list is the rows.
values = [
    ["Anna",  5, 4, 5],
    ["Piotr", 3, 3, 4],
    ["Ola",   4, 5, 4],
    ["Marek", 2, 3, 4],
    ["Kasia", 5, 4, 5],
]
df_from_lists = pd.DataFrame(values, columns=["student", "maths", "physics", "english"])
print("From list of lists:")
print(df_from_lists)
print()

# 3) From a NumPy array — matches the md example exactly.
arr = np.array([
    [5, 4, 5],
    [3, 3, 4],
    [4, 5, 4],
    [2, 3, 4],
    [5, 4, 5],
])
df_from_np = pd.DataFrame(
    arr,
    columns=["maths", "physics", "english"],
    index=["Anna", "Piotr", "Ola", "Marek", "Kasia"],
)
print("From NumPy array (with custom index):")
print(df_from_np)
print()

# 4) set_index / reset_index — NOT covered in pandas.md, standard pandas API.
#    set_index("col") promotes a column to be the row index, returning a new frame.
df_indexed = df_from_dicts.set_index("student")
print("After set_index('student'):")
print(df_indexed)
print()

#    reset_index() undoes it — moves the index back into a regular column and
#    restores the default RangeIndex.
df_reset = df_indexed.reset_index()
print("After reset_index():")
print(df_reset)


# used 0.24$