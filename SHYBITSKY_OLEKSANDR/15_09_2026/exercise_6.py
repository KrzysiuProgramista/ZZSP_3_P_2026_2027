"""Exercise 6: adding computed columns to a DataFrame."""

import pandas as pd

grades_data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
# .copy() so the new columns land on our own table and never touch the source data.
df_grades = pd.DataFrame(grades_data).set_index("student").copy()

SUBJECT_COLUMNS = ["maths", "physics", "english"]
PASSING_AVERAGE = 3.0

print("Starting table:")
print(df_grades)

# 1. The mean across the three subjects, computed row by row (axis=1).
df_grades["average"] = df_grades[SUBJECT_COLUMNS].mean(axis=1)

# 2. A boolean column: the comparison is applied to the whole column at once.
df_grades["passed"] = df_grades["average"] >= PASSING_AVERAGE

# 3. idxmax(axis=1) returns, for each row, the COLUMN NAME holding the largest value.
#    Ties are broken by column order, so the first of the tied subjects wins.
df_grades["best_subject"] = df_grades[SUBJECT_COLUMNS].idxmax(axis=1)

print("\nTable with the three new columns:")
print(df_grades)
print("\nColumn types after the additions:")
print(df_grades.dtypes)

# 4. Sorted by the average, best student first.
print("\n4. Sorted by average, descending:")
print(df_grades.sort_values("average", ascending=False))

# sort_values returns a new table; df_grades itself keeps its original row order.
print("\nThe unsorted df_grades is unchanged:")
print(df_grades)

# A quick check that the new columns say what they should.
print("\nStudents who passed:", list(df_grades.loc[df_grades["passed"]].index))
print("Students who did not pass:", list(df_grades.loc[~df_grades["passed"]].index))
