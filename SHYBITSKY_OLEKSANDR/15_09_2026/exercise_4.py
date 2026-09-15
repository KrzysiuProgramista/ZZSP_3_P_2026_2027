"""Exercise 4: inspecting a DataFrame and computing column statistics."""

import pandas as pd

grades_data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(grades_data)

# 1. Three quick looks at the data.
print("1. head(2) - the first two rows:")
print(df_grades.head(2))
print("\ntail(2) - the last two rows:")
print(df_grades.tail(2))
print("\nsample(3) - three random rows (random_state keeps the draw reproducible):")
print(df_grades.sample(3, random_state=42))

# 2. One column, selected with a single string -> a SERIES.
maths_grades = df_grades["maths"]
print("\n2. df_grades['maths']:")
print(maths_grades)
print("type:", type(maths_grades))

# 3. Several columns, selected with a LIST of strings -> a DATAFRAME.
maths_and_physics = df_grades[["maths", "physics"]]
print("\n3. df_grades[['maths', 'physics']]:")
print(maths_and_physics)
print("type:", type(maths_and_physics))

# 4. The difference.
# df_grades["maths"]              -> a single string, so pandas returns ONE column:
#                                    a Series, one-dimensional, shape (5,), it has a .name.
# df_grades[["maths", "physics"]] -> a LIST of names, so pandas returns a TABLE:
#                                    a DataFrame, two-dimensional, shape (5, 2), it has .columns.
# The inner brackets are the list itself, they are not "double indexing".
# Asking for one column as a list, df_grades[["maths"]], still gives a DataFrame of shape (5, 1).
print("\n4. Shapes make the difference visible:")
print("df_grades['maths'].shape           ->", df_grades["maths"].shape)
print("df_grades[['maths']].shape         ->", df_grades[["maths"]].shape)
print("df_grades[['maths','physics']].shape ->", df_grades[["maths", "physics"]].shape)

# 5. Statistics of a single column. Each method reduces the Series to one number.
print("\n5. Statistics of the maths column:")
print("mean (average):", maths_grades.mean())
print("max  (best grade):", maths_grades.max())
print("min  (worst grade):", maths_grades.min())
print("sum  (all grades added up):", maths_grades.sum())
print("std  (spread around the mean):", maths_grades.std())

# 6. The same mean for every column at once.
#    numeric_only=True tells pandas to skip the text column "student"
#    instead of raising an error on it.
print("\n6. df_grades.mean(numeric_only=True) - one mean per numeric column:")
print(df_grades.mean(numeric_only=True))
print("type of the result:", type(df_grades.mean(numeric_only=True)))
# The result is a Series: the column names became its index, the means became its values.
