import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sales_df = pd.read_csv(BASE_DIR / "sales.csv")

print("=== First 5 rows ===")
print(sales_df.head(5))
print("\n=== Shape ===")
print(sales_df.shape)
print("\n=== Dtypes ===")
print(sales_df.dtypes)
print("\n=== Column names ===")
print(sales_df.columns.tolist())
print("\n=== Memory usage ===")
sales_df.info(memory_usage="deep")
