import numpy as np
import pandas as pd

# Z listy słowników (jeden słownik = jeden wiersz)
df_a = pd.DataFrame([
    {"student": "Anna", "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola", "maths": 4, "physics": 5, "english": 4},
])
print(df_a)

# Z listy list - nazwy kolumn podajemy przez columns=
df_b = pd.DataFrame(
    [["Anna", 5, 4, 5], ["Piotr", 3, 3, 4], ["Ola", 4, 5, 4]],
    columns=["student", "maths", "physics", "english"],
)
print(df_b)

# Z tablicy NumPy (jeden dtype dla całości, kolumny domyślnie 0,1,2 - nadajemy nazwy)
arr = np.array([[5, 4, 5], [3, 3, 4], [4, 5, 4]])
df_c = pd.DataFrame(arr, columns=["maths", "physics", "english"])
print(df_c)

# set_index i reset_index
df_idx = df_a.set_index("student")
print(df_idx)
print(df_idx.loc["Ola"])   # teraz można wybierać wiersz po imieniu

df_back = df_idx.reset_index()
print(df_back)
