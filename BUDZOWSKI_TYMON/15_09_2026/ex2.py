import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

df_grades = pd.DataFrame(data)
print(df_grades)

print(df_grades.shape)
print(df_grades.columns)
print(df_grades.index)
print(df_grades.dtypes)

df_grades.info()

print(df_grades.describe())