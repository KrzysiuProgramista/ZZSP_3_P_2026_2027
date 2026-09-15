"""Exercise 5: a first real question - one pandas expression per answer."""

import pandas as pd

grades_data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(grades_data).set_index("student")

SUBJECT_COLUMNS = ["maths", "physics", "english"]

print("The table (students in the index, so every answer can name them):")
print(df_grades)

# 1. The class average in maths: one column reduced to one number.
print("\n1. Class average in maths:")
print(df_grades["maths"].mean())

# 2. The best physics score: idxmax returns the INDEX LABEL of the largest value,
#    which is exactly the student's name because "student" is the index.
print("\n2. Highest score in physics:")
print(df_grades["physics"].idxmax())

# 3. Each student's average across the three subjects.
#    axis=1 means "walk across the columns, one row at a time".
print("\n3. Average per student (axis=1 - across the row):")
print(df_grades[SUBJECT_COLUMNS].mean(axis=1))

# 4. How many students got a 5 in english.
#    The comparison makes a boolean Series, and sum() counts the True values.
print("\n4. Number of students with a 5 in english:")
print((df_grades["english"] == 5).sum())

# 5. The average of every grade in the whole table.
#    stack() lays all three subject columns into one long Series, then mean() averages it.
print("\n5. Average of all grades in the table:")
print(df_grades[SUBJECT_COLUMNS].stack().mean())
