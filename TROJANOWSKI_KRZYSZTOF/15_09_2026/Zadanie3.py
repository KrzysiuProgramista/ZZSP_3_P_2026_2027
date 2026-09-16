import numpy as np
import pandas as pd

# List of dictionaries
data_dict = [
    {"student": "Anna", "maths": 5, "physics": 4, "english": 5},
    {"student": "Piotr", "maths": 3, "physics": 3, "english": 4},
    {"student": "Ola", "maths": 4, "physics": 5, "english": 4},
    {"student": "Marek", "maths": 2, "physics": 3, "english": 4},
    {"student": "Kasia", "maths": 5, "physics": 4, "english": 5}
]

# Create DataFrame from list of dictionaries
df_from_dict = pd.DataFrame(data_dict)
print("DataFrame from list of dictionaries:")
print(df_from_dict)

# List of lists
data_list = [
    ["Anna", 5, 4, 5],
    ["Piotr", 3, 3, 4],
    ["Ola", 4, 5, 4],
    ["Marek", 2, 3, 4],
    ["Kasia", 5, 4, 5]
]

# Create DataFrame from list of lists
df_from_list = pd.DataFrame(data_list, columns=["student", "maths", "physics", "english"])
print("DataFrame from list of lists:")
print(df_from_list)

# NumPy array
data_array = np.array([
    ["Anna", 5, 4, 5],
    ["Piotr", 3, 3, 4],
    ["Ola", 4, 5, 4],
    ["Marek", 2, 3, 4],
    ["Kasia", 5, 4, 5]
])

# Create DataFrame from NumPy array
df_from_array = pd.DataFrame(data_array, columns=["student", "maths", "physics", "english"])
print("DataFrame from NumPy array:")
print(df_from_array)

# Set "student" column as the index
df_set_index = df_from_dict.set_index("student")
print("DataFrame with 'student' as index:")
print(df_set_index)

# Reset index
df_reset_index = df_set_index.reset_index()
print("DataFrame after resetting index:")
print(df_reset_index)
