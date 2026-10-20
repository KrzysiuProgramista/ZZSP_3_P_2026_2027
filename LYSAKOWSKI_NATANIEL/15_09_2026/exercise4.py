import pandas as pd

# Re-creating df_grades from Exercise 2 to ensure the execution context is perfect
data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}

df_grades = pd.DataFrame(data)

print("=========================================")
print("       Exercise 4: Inspecting df_grades    ")
print("=========================================\n")

# 1. Head, Tail, Sample views
print("\n--- df_grades.head(2) ---")
print(df_grades.head(2))

print("\n--- df_grades.tail(2) ---")
print(df_grades.tail(2))

print("\n--- df_grades.sample(3) ---")
print(df_grades.sample(3))

# 2. Selecting Series vs DataFrame (The key difference)
print("\n=========================================")

# df["maths"] - returns a Pandas Series (a single column viewed as a series object)
series_maths = df_grades["maths"]
print("\n--- Type of df[\"maths\"] ---")
print(type(series_maths))

# df[["maths", "physics"]] - returns a Pandas DataFrame (a slice of the table)
dataframe_slice = df_grades[["maths", "physics"]]
print("\n--- Type of df[\"maths\", \"physics\"] ---")
print(type(dataframe_slice))

# The difference is that the first selects a Series (a 1-dimensional array), while the second selects a DataFrame (a 2-dimensional table).

# 3. Series Operations
print("\n=========================================")
print("       --- df_grades[\"maths\"] Operations ---")
# Select the Series for operations
series_to_operate = df_grades["maths"]

print("\n--- Mean ---")
print(series_to_operate.mean()) # Calculate the average

print("\n--- Max ---")
print(series_to_operate.max()) # Find the highest score

print("\n--- Min ---")
print(series_to_operate.min()) # Find the lowest score

print("\n--- Sum ---")
print(series_to_operate.sum()) # Total sum of all scores

print("\n--- Std Dev ---")
print(series_to_operate.std()) # Measure of data dispersion

# 4. DataFrame Operations
print("\n=========================================")
print("       --- df_grades Aggregate ---")

# Calculate mean across all numeric columns at once
print("\n--- df.mean(numeric_only=True) ---")
# Note: We only need to call it on the object, not pass numeric_only=True again if we are sure data is clean
print(df_grades.mean())