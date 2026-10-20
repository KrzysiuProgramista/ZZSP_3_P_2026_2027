import numpy as np
import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

df_grades = pd.DataFrame(data)

# Print the DataFrame
print(df_grades)

# Print DataFrame shape, columns, index, and dtypes
print("Shape:", df_grades.shape)
print("Columns:", df_grades.columns)
print("Index:", df_grades.index)
print("Dtypes:", df_grades.dtypes)

# Print DataFrame info
print(df_grades.info())
# Read every line of the output
# The output includes the number of non-null entries in each column, memory usage, and detailed information about the DataFrame.

# Print DataFrame description
print(df_grades.describe())
# Explain what each row of the output means
# The first row shows the count of non-null values for each column.
# The second row shows the mean of each column.
# The third row shows the standard deviation of each column.
# The fourth row shows the minimum value in each column.
# The fifth row shows the 25th percentile (first quartile) of each column.
# The sixth row shows the 50th percentile (median) of each column.
# The seventh row shows the 75th percentile (third quartile) of each column.
# The eighth row shows the maximum value in each column.
