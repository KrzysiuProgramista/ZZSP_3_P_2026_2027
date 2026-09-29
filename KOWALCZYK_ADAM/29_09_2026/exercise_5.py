import pandas as pd

# Exercise 5: Writing files
sales_df = pd.read_csv("sales.csv")

# 1. Write to CSV without index
sales_df.to_csv("sales_clean.csv", index=False)

# 2. Write to JSON with orient="records"
sales_df.to_json("sales_clean.json", orient="records")

# 3. Write to Excel
try:
    sales_df.to_excel("sales_clean.xlsx", sheet_name="Sheet1", index=False)
    print("Successfully wrote sales_clean.xlsx")
except ModuleNotFoundError:
    print("Skipped writing Excel file: openpyxl is not installed.")

# Read them back and confirm
df_csv = pd.read_csv("sales_clean.csv")
df_json = pd.read_json("sales_clean.json", orient="records")

print("\nRead back CSV shape:", df_csv.shape)
print("Read back JSON shape:", df_json.shape)

# Read back Excel (Dodane)
try:
    df_excel = pd.read_excel("sales_clean.xlsx", sheet_name="Sheet1")
    print("Read back Excel shape:", df_excel.shape)
except Exception as e:
    print(f"Skipped reading Excel file: {e}")