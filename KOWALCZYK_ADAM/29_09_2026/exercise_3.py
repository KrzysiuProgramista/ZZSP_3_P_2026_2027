import pandas as pd

# Exercise 3: A first-pass inspection routine
def inspect(df):
    print("--- Shape ---")
    print(df.shape)
    
    print("\n--- Columns and Dtypes ---")
    print(df.dtypes)
    
    print("\n--- Missing Values (Count & Percentage) ---")
    missing = pd.isna(df).sum()
    missing_pct = pd.isna(df).mean() * 100
    print(pd.DataFrame({"count": missing, "percentage": missing_pct}))
    
    print("\n--- Duplicate Rows ---")
    print("Total duplicates:", df.duplicated().sum())
    
    print("\n--- Numeric Columns Summary ---")
    print(df.describe())
    
    print("\n--- Object Columns Summary ---")
    for col in df.columns:
        if df[col].dtype == "object":
            print(f"\nColumn: {col}")
            print(f"Unique values: {df[col].nunique()}")
            print(f"Top 3 common:\n{df[col].value_counts().head(3)}")

print("====== INSPECTING sales.csv ======")
inspect(pd.read_csv("sales.csv"))

print("\n====== INSPECTING sales_pl.csv ======")
sales_pl = pd.read_csv("sales_pl.csv", sep=";", decimal=",")
inspect(sales_pl)
