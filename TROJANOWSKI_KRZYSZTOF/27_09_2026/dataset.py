import numpy as py
import pandas as pd

def inspect(df):
    """First-pass inspection routine for any DataFrame."""
    print("=" * 60)
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    print("\nColumns and dtypes:")
    for col, dt in df.dtypes.items():
        print(f"  {col:<25} {dt}")

    print("\nMissing values:")
    missing = df.isna().sum()
    pct = (missing / len(df) * 100).round(2) if len(df) else missing * 0
    print(pd.DataFrame({"missing": missing, "percent": pct}).to_string())

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    num = df.select_dtypes("number")
    if not num.empty:
        print("\nNumeric columns:")
        print(num.agg(["min", "max", "mean", "median"]).T.to_string())

    obj = df.select_dtypes(include=["object", "string"])
    if not obj.empty:
        print("\nText columns:")
        for col in obj:
            top3 = obj[col].value_counts().head(3).to_dict()
            print(f"  {col}: {obj[col].nunique()} unique, top 3: {top3}")
    print("=" * 60)

df = pd.read_csv("netflix_customer_churn.csv")

inspect(df)