import numpy as np
import pandas as pd

# Load data from previous exercise
data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5]
}
df_grades = pd.DataFrame(data)

# Using df_grades
print("df.head(2):")
print(df_grades.head(2))
print("df.tail(2):")
print(df_grades.tail(2))
print("df.sample(3):")
print(df_grades.sample(3))

# What type is df["maths"]?
maths_series = df_grades["maths"]
print("Type of df[\"maths\"]:")
print(type(maths_series))
# Explanation: This is a pandas Series object containing the "maths" column of the DataFrame.

# What type is df[["maths", "physics"]]?
maths_physics_df = df_grades[["maths", "physics"]]
print("Type of df[\"maths\", \"physics\"]:")
print(type(maths_physics_df))
# Explanation: This is a pandas DataFrame object containing the "maths" and "physics" columns of the original DataFrame.

# Calculate mean, max, min, sum, and std for "maths" column
print("Mean of 'maths':", df_grades["maths"].mean())
print("Max of 'maths':", df_grades["maths"].max())
print("Min of 'maths':", df_grades["maths"].min())
print("Sum of 'maths':", df_grades["maths"].sum())
print("Standard deviation of 'maths':", df_grades["maths"].std())

# Calculate mean of every column at once
print("Mean of all columns (numeric only):")
print(df_grades.mean(numeric_only=True))
