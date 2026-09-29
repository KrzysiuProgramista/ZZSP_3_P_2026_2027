import pandas as pd

# Exercise 1: Basic CSV reading
sales_df = pd.read_csv("sales.csv")

print("--- First 5 rows ---")
print(sales_df.head(5))

print("\n--- Shape ---")
print(sales_df.shape)

print("\n--- Dtypes ---")
print(sales_df.dtypes)

print("\n--- Column names ---")
print(sales_df.columns)

print("\n--- Memory Usage (deep) ---")
sales_df.info(memory_usage="deep")
