import numpy as np
import pandas as pd

# Shared data: values per student + score columns.
students = ["Anna", "Piotr", "Ola", "Marek", "Kasia"]
maths = [5, 3, 4, 2, 5]
physics = [4, 3, 5, 3, 4]
english = [5, 4, 4, 4, 5]

columns = ["student", "maths", "physics", "english"]  # fixed column order

# 1. From a list of dictionaries (one dict = one row).
#    Column order follows the first dict's insertion order.
data_list_of_dicts = [
    {"student": "Anna", "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola", "maths": 4, "physics": 5, "english": 4},
    {"student": "Marek", "maths": 2, "physics": 3, "english": 4},
    {"student": "Kasia", "maths": 5, "physics": 4, "english": 5},
]
df_list_of_dicts = pd.DataFrame(data_list_of_dicts)

# 2. From a list of lists, passing columns=[...] to fix the column order.
#    Each inner list is a row whose values are aligned to `columns`.
data_rows = [students, maths, physics, english]
df_list_of_lists = pd.DataFrame(data_rows, columns=columns)

# 3. From a NumPy array (values are in the same order as `columns`).
df_numpy = pd.DataFrame(np.array(data_rows), columns=columns)

# 4. Make the "student" column the index, then reset it back to a regular column.
df_indexed = df_list_of_dicts.copy()
df_indexed = df_indexed.set_index("student")
df_indexed = df_indexed.reset_index()
