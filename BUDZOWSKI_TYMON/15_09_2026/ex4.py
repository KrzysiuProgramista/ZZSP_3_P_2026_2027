import pandas as pd

df_grades = pd.DataFrame({
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
})

print(df_grades.head(2))
print(df_grades.tail(2))
print(df_grades.sample(3, random_state=42))

maths = df_grades["maths"]
print(type(maths))
print(maths)

two_cols = df_grades[["maths", "physics"]]
print(type(two_cols))
print(two_cols)

# df["maths"] (single label) returns a Series: one 1-D column with the index and a name.
# df[["maths", "physics"]] (list of labels) returns a DataFrame: a 2-D table, even if the list has one element.

print(df_grades["maths"].mean())
print(df_grades["maths"].max())
print(df_grades["maths"].min())
print(df_grades["maths"].sum())
print(df_grades["maths"].std())

print(df_grades.mean(numeric_only=True))