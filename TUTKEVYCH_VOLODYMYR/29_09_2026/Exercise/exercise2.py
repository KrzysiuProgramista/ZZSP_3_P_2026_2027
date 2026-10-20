import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sales_pl_df = pd.read_csv(BASE_DIR / "sales_pl.csv", sep=";", decimal=",")

sales_pl_df = sales_pl_df.rename(columns={
    "data": "date",
    "produkt": "product",
    "kategoria": "category",
    "region": "region",
    "ilosc": "quantity",
    "cena_jednostkowa": "unit_price"
})

print("=== Data ===")
print(sales_pl_df)
print("\n=== Dtypes ===")
print(sales_pl_df.dtypes)

numeric_columns = ["quantity", "unit_price"]
assert all(pd.api.types.is_numeric_dtype(sales_pl_df[c]) for c in numeric_columns)
print("\nNumeric columns are numeric.")
