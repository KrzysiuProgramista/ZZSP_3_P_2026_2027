# Exercise 3: Other ways to build a DataFrame**

import pandas as pd

# From a list of dictionaries (one dict per row)
data_dicts = [
    {"student": "Anna", "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola", "maths": 4, "physics": 5, "english": 4},
    {"student": "Marek", "maths": 2, "physics": 3, "english": 4},
    {"student": "Kasia", "maths": 5, "physics": 4, "english": 5},
]
df_dict = pd.DataFrame(data_dicts)
print(df_dict)

# From a list of lists, passing columns=[...]
data_lists = [
    ["Anna", 5, 4, 5],
    ["Piotr", 3, 3, 4],
    ["Ola", 4, 5, 4],
    ["Marek", 2, 3, 4],
    ["Kasia", 5, 4, 5],
]
df_lists = pd.DataFrame(data_lists, columns=["student", "maths", "physics", "english"])
print(df_lists)

# From a NumPy array
data_array = np.array([
    ["Anna", 5, 4, 5],
    ["Piotr", 3, 3, 4],
    ["Ola", 4, 5, 4],
    ["Marek", 2, 3, 4],
    ["Kasia", 5, 4, 5],
])
df_array = pd.DataFrame(data_array, columns=["student", "maths", "physics", "english"])
print(df_array)

# Set the "student" column as the index with set_index, then reset it
df_indexed = df_grades.set_index("student")
print(df_indexed)
df_reset_index = df_indexed.reset_index()
print(df_reset_index)
