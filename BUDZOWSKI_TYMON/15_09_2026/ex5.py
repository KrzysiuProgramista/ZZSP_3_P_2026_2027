import pandas as pd

df_grades = pd.DataFrame({
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
})

print(df_grades["maths"].mean())

print(df_grades.set_index("student")["physics"].idxmax())

print(df_grades.set_index("student").mean(axis=1))

print((df_grades["english"] == 5).sum())

print(df_grades.set_index("student").stack().mean())