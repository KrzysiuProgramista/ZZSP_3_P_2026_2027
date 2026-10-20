# Exercise 2: DataFrame from a dictionary**

import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

df_grades = pd.DataFrame(data)
print(df_grades)

print(df_grades.shape)
print(df_grades.columns)
print(df_grades.index)
print(df_grades.dtypes)

print(df_grades.info())
# Output:
# <class 'pandas.core.frame.DataFrame'>
# RangeIndex: 5 entries, 0 to 4
# Data columns (total 4 columns):
#  student    5 non-null object
#  maths       5 non-null int64
#  physics     5 non-null int64
#  english     5 non-null int64
# dtypes: int64(3), object(1)
# memory usage: 160.0+ bytes

print(df_grades.describe())
# Output:
#           maths  physics  english
# count     5.000     5.000     5.000
# mean      3.800     3.600     4.200
# std       1.549     1.191     0.549
# min       2.000     3.000     4.000
# 25%       3.000     3.000     4.000
# 50%       4.000     3.000     4.000
# 75%       5.000     4.000     4.000
# max       5.000     5.000     5.000

# Explanation of the output:
#   - count: number of non-NA observations
#   - mean: mean of the values
#   - std: standard deviation of the values
#   - min: minimum value
#   - 25%, 50%, 75%: percentiles
#   - max: maximum value

