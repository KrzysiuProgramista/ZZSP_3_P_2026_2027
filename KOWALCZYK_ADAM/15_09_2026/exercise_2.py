import numpy as np
import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

# Per the notes: "From a dict, the keys become the column labels and the values
# become the columns."
df_grades = pd.DataFrame(data)

print("df_grades:")
print(df_grades)
print()

print("df.shape   :", df_grades.shape)     # (rows, columns)
print("df.columns :", df_grades.columns)   # column labels
print("df.index   :", df_grades.index)     # row labels (default RangeIndex here)
print("df.dtypes  :")
print(df_grades.dtypes)                    # dtype per column (see md: "keeps a dtype per column")
print()

print("df.info():")
df_grades.info()
print()
# info() lines, top to bottom:
#   1. class of the object (DataFrame)
#   2. the index type + range of row labels
#   3. number of columns
#   4. per-column table: index, name, non-null count, dtype
#   5. dtype tally (how many columns of each dtype)
#   6. memory usage of the frame

print("df.describe():")
print(df_grades.describe())
print()
# describe() rows, top to bottom (numeric columns only — 'student' is skipped):
#   count : how many non-missing values in the column
#   mean  : arithmetic average of the values
#   std   : standard deviation — how spread out the values are around the mean
#   min   : smallest value
#   25%   : first quartile (25% of values are at or below this)
#   50%   : median (half the values are at or below this)
#   75%   : third quartile (75% of values are at or below this)
#   max   : largest value


# used about 0.15$