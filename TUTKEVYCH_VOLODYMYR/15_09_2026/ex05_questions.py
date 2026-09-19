import numpy as np
import pandas as pd

df_grades = pd.DataFrame({
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
})
subjects = ["maths", "physics", "english"]

# 1. Średnia klasy z matematyki
print(df_grades["maths"].mean())

# 2. Kto ma najwyższą ocenę z fizyki (idxmax zwraca etykietę indeksu -> imię przez .loc)
print(df_grades.loc[df_grades["physics"].idxmax(), "student"])

# 3. Średnia każdego ucznia z trzech przedmiotów (axis=1 = po wierszach)
print(df_grades[subjects].mean(axis=1))

# 4. Ilu uczniów dostało 5 z angielskiego
print((df_grades["english"] == 5).sum())

# 5. Średnia wszystkich ocen w całej tabeli
print(df_grades[subjects].to_numpy().mean())
