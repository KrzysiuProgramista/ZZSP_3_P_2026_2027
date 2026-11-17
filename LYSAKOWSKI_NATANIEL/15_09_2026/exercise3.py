import pandas as pd
import numpy as np

# --- 1. From a list of dictionaries (one dict per row) ---
data_dict = [
    {"student": "Anna", "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola", "maths": 4, "physics": 5, "english": 4},
    {"student": "Marek", "maths": 2, "physics": 3, "english": 4},
    {"student": "Kasia", "maths": 5, "physics": 4, "english": 5},
]

print("=========================================")
print("       Exercise 3: DataFrame Output     ")
print("=========================================\n")

# Create DataFrame from list of dicts
df_from_dict = pd.DataFrame(data_dict)
print("--- 1. From List of Dictionaries ---")
print(df_from_dict)

# Set "student" as index and then reset it
print("\n--- Setting 'student' Index, Resetting ---")
df_indexed = df_from_dict.set_index("student")
print("After set_index(\"student\"):\n", df_indexed)

df_reset = df_indexed.reset_index()
print("\nAfter reset_index():\n", df_reset)


# --- 2. From a list of lists, passing columns=[...] ---
data_list = [
    [5, 3, 4, 2, 5], # Anna's scores
    [4, 3, 5, 3, 4], # Piotr's scores
    [5, 4, 4, 4, 5], # Ola's scores
    [2, 3, 4, 4, 5], # Marek's scores
    [5, 3, 4, 2, 5]  # Kasia's scores
]

column_names = ["maths", "physics", "english"] # Note: 5 columns are provided, only 3 names given. Truncating for coherence with previous data structure example length issue.
# Assuming the input list was intended to match the 3 subject scores:
data_list_corrected = [
    [5, 4, 5], # Anna: M, P, E
    [3, 3, 4], # Piotr
    [4, 5, 4], # Ola
    [2, 3, 4], # Marek
    [5, 4, 5]  # Kasia
]

df_from_list = pd.DataFrame(data_list_corrected, columns=column_names)
print("\n\n--- 2. From List of Lists ---")
print(df_from_list)


# --- 3. From a NumPy array ---
array_data = np.array([
    [5, 4, 5], [3, 3, 4], [4, 5, 4], [2, 3, 4], [5, 4, 5]
])

# Create DataFrame from NumPy array and specify columns/index for clarity
df_from_numpy = pd.DataFrame(array_data, columns=column_names)
print("\n\n--- 3. From NumPy Array ---")
print(df_from_numpy)