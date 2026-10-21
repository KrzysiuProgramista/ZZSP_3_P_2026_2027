import numpy as np
import pandas as pd

rows = [
    {"student": "Anna", "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola", "maths": 4, "physics": 5, "english": 4},
    {"student": "Marek", "maths": 2, "physics": 3, "english": 4},
    {"student": "Kasia", "maths": 5, "physics": 4, "english": 5},
]
df_from_dicts = pd.DataFrame(rows)
print(df_from_dicts)

lists = [
    ["Anna", 5, 4, 5],
    ["Piotr", 3, 3, 4],
    ["Ola", 4, 5, 4],
    ["Marek", 2, 3, 4],
    ["Kasia", 5, 4, 5],
]
df_from_lists = pd.DataFrame(lists, columns=["student", "maths", "physics", "english"])
print(df_from_lists)

arr = np.array([[5, 4, 5], [3, 3, 4], [4, 5, 4], [2, 3, 4], [5, 4, 5]])
df_from_numpy = pd.DataFrame(
    arr,
    columns=["maths", "physics", "english"],
    index=["Anna", "Piotr", "Ola", "Marek", "Kasia"],
)
print(df_from_numpy)

df_indexed = df_from_dicts.set_index("student")
print(df_indexed)
print(df_indexed.index)

df_reset = df_indexed.reset_index()
print(df_reset)
print(df_reset.index)