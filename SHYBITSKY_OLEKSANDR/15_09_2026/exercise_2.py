"""Exercise 2: building a DataFrame from a dictionary and inspecting it."""

import pandas as pd

# The dictionary KEYS become the column names,
# the dictionary VALUES (the lists) become the columns themselves.
grades_data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths": [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(grades_data)

# 1. The table itself.
print("1. df_grades:")
print(df_grades)

# 2. The four attributes that describe the shape of the table.
print("\n2. Basic attributes:")
print("shape   (rows, columns):", df_grades.shape)
print("columns (the column labels):", list(df_grades.columns))
print("index   (the row labels):", list(df_grades.index))
print("dtypes  (the type of each column):")
print(df_grades.dtypes)

# 3. info() prints a technical summary. It returns None, so it is CALLED, not printed.
print("\n3. df_grades.info():")
df_grades.info()
# Reading that output line by line:
#   <class 'pandas.DataFrame'>  -> the object type
#   RangeIndex: 5 entries, 0 to 4 -> 5 rows, labelled with the default index 0..4
#   Data columns (total 4 columns) -> how many columns follow
#   #  Column  Non-Null Count  Dtype -> the header of the per-column table
#   0  student   5 non-null  str     -> the text column, no missing values
#   1  maths     5 non-null  int64   -> whole numbers, no missing values
#   2  physics   5 non-null  int64
#   3  english   5 non-null  int64
#   "5 non-null" in every row means nothing is missing: 5 rows, 5 real values.
#   dtypes: ... -> a count of the column types
#   memory usage: ... -> how much RAM the table occupies

# 4. describe() gives the statistics of the NUMERIC columns only.
print("\n4. df_grades.describe():")
print(df_grades.describe())
# What each ROW of that output means (each computed per column):
#   count -> how many non-missing values the column holds (5 grades in each subject)
#   mean  -> the arithmetic average of the column
#   std   -> the standard deviation, i.e. how widely the grades spread around the mean;
#            a small std means everybody scored similarly, a large one means they differ
#   min   -> the lowest grade in the column
#   25%   -> the first quartile: 25% of the grades are below this value
#   50%   -> the median: the middle grade once they are sorted
#   75%   -> the third quartile: 75% of the grades are below this value
#   max   -> the highest grade in the column
# The "student" column is missing from the output because it is text, not numbers.
print("\ndescribe(include='all') also covers the text column:")
print(df_grades.describe(include="all"))
# For the text column pandas reports different rows instead:
#   unique -> how many different names appear, top -> the most frequent one,
#   freq   -> how many times that most frequent value occurs.
