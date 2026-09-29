import pandas as pd
import time

# Exercise 6: Only what you need

# Timing the subset read (Dodane)
start_time_subset = time.perf_counter()
df_subset = pd.read_csv(
    "sales.csv", 
    usecols=["date", "product", "quantity"], 
    nrows=10
)
end_time_subset = time.perf_counter()
time_subset = end_time_subset - start_time_subset

print("--- Subset Info ---")
print(df_subset.info())

# Timing the full file read
start_time_full = time.perf_counter()
_ = pd.read_csv("sales.csv")
end_time_full = time.perf_counter()
time_full = end_time_full - start_time_full

# Porównanie czasów (Dodane)
print(f"\nTime taken to read subset: {time_subset:.6f} seconds")
print(f"Time taken to read full file: {time_full:.6f} seconds")
print(f"Difference (subset is faster by): {time_full - time_subset:.6f} seconds")