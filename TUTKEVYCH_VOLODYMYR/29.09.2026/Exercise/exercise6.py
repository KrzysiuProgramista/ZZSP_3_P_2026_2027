import pandas as pd
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sales_path = BASE_DIR / "sales.csv"

# The supplied sales.csv contains unit_price rather than amount.
# For this exercise, amount is created as quantity * unit_price.
sales_df = pd.read_csv(sales_path)
sales_df["amount"] = sales_df["quantity"] * sales_df["unit_price"]

print("=== 1. Only date, product and amount ===")
selected_df = pd.read_csv(
    sales_path,
    usecols=["date", "product", "quantity", "unit_price"]
)
selected_df["amount"] = selected_df["quantity"] * selected_df["unit_price"]
selected_df = selected_df[["date", "product", "amount"]]
print(selected_df)

print("\n=== 2. First 10 rows ===")
first_10_df = pd.read_csv(sales_path, nrows=10)
first_10_df["amount"] = first_10_df["quantity"] * first_10_df["unit_price"]
print(first_10_df)

print("\n=== 3. Timing full-file read ===")
start = time.perf_counter()
for _ in range(100):
    pd.read_csv(sales_path)
elapsed = time.perf_counter() - start
print(f"100 full-file reads: {elapsed:.6f} seconds")
print(f"Average full-file read: {elapsed / 100:.6f} seconds")

print("\nNote: in a Jupyter notebook the equivalent is:")
print("%timeit pd.read_csv('sales.csv')")
