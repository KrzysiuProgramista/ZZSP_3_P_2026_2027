"""Exercise 3: the other ways of building the same DataFrame."""

import numpy as np
import pandas as pd

GRADE_COLUMNS = ["student", "maths", "physics", "english"]

# 1. From a LIST OF DICTIONARIES - one dictionary per ROW.
#    Every key found becomes a column; a key missing from a row would become NaN there.
grade_records = [
    {"student": "Anna", "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola", "maths": 4, "physics": 5, "english": 4},
    {"student": "Marek", "maths": 2, "physics": 3, "english": 4},
    {"student": "Kasia", "maths": 5, "physics": 4, "english": 5},
]
df_from_records = pd.DataFrame(grade_records)
print("1. From a list of dictionaries (one dict = one row):")
print(df_from_records)

# 2. From a LIST OF LISTS - the rows carry no names, so the columns must be named.
grade_rows = [
    ["Anna", 5, 4, 5],
    ["Piotr", 3, 3, 4],
    ["Ola", 4, 5, 4],
    ["Marek", 2, 3, 4],
    ["Kasia", 5, 4, 5],
]
df_from_rows = pd.DataFrame(grade_rows, columns=GRADE_COLUMNS)
print("\n2. From a list of lists with columns=[...]:")
print(df_from_rows)
# Without columns=[...] pandas would number the columns 0, 1, 2, 3 and the meaning
# of each column would be lost.

# 3. From a NUMPY ARRAY - useful when the numbers already live in NumPy.
#    The three subjects are numeric, so they form a clean 5x3 array of integers.
student_names = ["Anna", "Piotr", "Ola", "Marek", "Kasia"]
grade_matrix = np.array(
    [
        [5, 4, 5],
        [3, 3, 4],
        [4, 5, 4],
        [2, 3, 4],
        [5, 4, 5],
    ]
)
df_from_array = pd.DataFrame(
    grade_matrix,
    columns=["maths", "physics", "english"],
    index=student_names,
)
print("\n3. From a NumPy array (the names were passed as the index):")
print(df_from_array)
print("shape of the array:", grade_matrix.shape, "-> shape of the DataFrame:", df_from_array.shape)

# 4. set_index moves a COLUMN into the index; reset_index moves it back.
df_grades = df_from_records
df_indexed_by_student = df_grades.set_index("student")
print("\n4. After set_index('student') - 'student' is no longer a column:")
print(df_indexed_by_student)
print("columns now:", list(df_indexed_by_student.columns))
print("index now:", list(df_indexed_by_student.index))
print("\nRows can now be selected by name with .loc:")
print(df_indexed_by_student.loc["Ola"])

df_back_to_default = df_indexed_by_student.reset_index()
print("\nAfter reset_index() - 'student' is an ordinary column again,")
print("and the default RangeIndex 0..4 is back:")
print(df_back_to_default)
print("columns now:", list(df_back_to_default.columns))

# set_index and reset_index return NEW DataFrames; df_grades itself was never modified.
print("\nThe original df_grades is untouched:")
print(df_grades)
