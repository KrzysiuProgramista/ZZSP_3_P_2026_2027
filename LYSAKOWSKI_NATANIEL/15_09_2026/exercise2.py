import pandas as pd

# Data from the exercise
data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

# Create the DataFrame
df_grades = pd.DataFrame(data)

print("=========================================")
print("       Exercise 2: DataFrame Output     ")
print("=========================================\n")

# Print the entire frame (matches "Print it.")
print("--- df_grades ---")
# Use to_string for predictable console output of the whole thing.
print(df_grades.to_string()) 

# Print structure attributes
print("\n--- df.shape ---")
print(df_grades.shape)

print("\n--- df.columns ---")
print(df_grades.columns)

print("\n--- df.index ---")
print(df_grades.index)

print("\n--- df.dtypes ---")
print(df_grades.dtypes)

# Print info() output (read every line of the output.)
print("\n--- df.info() Output ---")
df_grades.info()

# Print describe() output (and explanation follows execution)
print("\n--- df.describe() Output ---")
description = df_grades.describe()
print(description)

# Providing the explanation of describe()'s rows as requested by the exercise prompt
print("\n=========================================")
print("       README: Explanation of df.describe() Output     ")
print("=========================================")
print("- The rows (index) are aggregation functions: 'count' tracks non-null entries; 'mean' is the average score per subject; 'std' is the standard deviation (data spread); and 'min'/'max' are the lowest/highest scores.")
print("- The columns correspond to the subjects: 'maths', 'physics', and 'english'.")