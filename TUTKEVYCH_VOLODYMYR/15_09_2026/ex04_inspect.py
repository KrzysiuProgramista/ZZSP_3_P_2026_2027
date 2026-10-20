import numpy as np
import pandas as pd

df_grades = pd.DataFrame({
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
})

print(df_grades.head(2))
print(df_grades.tail(2))
print(df_grades.sample(3))

print(type(df_grades["maths"]))               # pandas.Series
print(type(df_grades[["maths", "physics"]]))  # pandas.DataFrame
# Różnica: df["maths"] (pojedyncza etykieta) zwraca Series - jedną kolumnę (1-D),
# a df[["maths", "physics"]] (LISTA etykiet) zwraca DataFrame - tabelę (2-D),
# nawet gdyby na liście była tylko jedna kolumna.

print(df_grades["maths"].mean())
print(df_grades["maths"].max())
print(df_grades["maths"].min())
print(df_grades["maths"].sum())
print(df_grades["maths"].std())

# Średnia każdej kolumny liczbowej naraz ("student" pomijamy)
print(df_grades.mean(numeric_only=True))
