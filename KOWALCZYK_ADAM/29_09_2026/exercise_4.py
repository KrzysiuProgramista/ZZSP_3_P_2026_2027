import pandas as pd
import json

# Exercise 4: Reading JSON
with open("products.json", "r") as f:
    data = json.load(f)

# Native loading (nested objects become dictionaries in the cell)
df_nested = pd.DataFrame(data)

# Flattened loading
df_flat = pd.json_normalize(data)

print("--- Nested DataFrame ---")
print(df_nested.head(2))

print("\n--- Flattened DataFrame ---")
print(df_flat.head(2))
