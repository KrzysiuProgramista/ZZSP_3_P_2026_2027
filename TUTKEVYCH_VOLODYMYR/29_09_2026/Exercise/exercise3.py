import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def inspect(df):
    print("=" * 60)
    print("Shape:", df.shape)
    print("\nColumns and dtypes:")
    for column, dtype in df.dtypes.items():
        print(f"  {column}: {dtype}")

    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percent": (df.isna().mean() * 100).round(2)
    })
    print("\nMissing values:")
    print(missing)
    print("\nDuplicate rows:", df.duplicated().sum())

    numeric_columns = df.select_dtypes(include="number").columns
    if len(numeric_columns):
        print("\nNumeric columns:")
        print(pd.DataFrame({
            "min": df[numeric_columns].min(),
            "max": df[numeric_columns].max(),
            "mean": df[numeric_columns].mean(),
            "median": df[numeric_columns].median()
        }))

    object_columns = df.select_dtypes(include="object").columns
    print("\nObject columns:")
    for column in object_columns:
        print(f"\n{column}:")
        print("  unique values:", df[column].nunique(dropna=True))
        print("  3 most common:")
        print(df[column].value_counts(dropna=True).head(3))

sales_df = pd.read_csv(BASE_DIR.parent / "sales.csv")
sales_pl_df = pd.read_csv(BASE_DIR / "sales_pl.csv", sep=";", decimal=",").rename(columns={
    "data": "date", "produkt": "product", "kategoria": "category",
    "region": "region", "ilosc": "quantity", "cena_jednostkowa": "unit_price"
})

print("INSPECTION: sales.csv")
inspect(sales_df)
print("\nINSPECTION: sales_pl.csv")
inspect(sales_pl_df)
