import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

messy_df = pd.read_csv(
    BASE_DIR / "messy.csv",
    sep=";",                         # fields are separated by semicolons
    skiprows=2,                      # first two lines are junk metadata
    na_values=["n/a", "-", "brak", ""],  # all listed missing-value markers
    keep_default_na=True
)

# Clean the currency-formatted price and convert it to numeric.
messy_df["price"] = (
    messy_df["price"]
    .astype("string")
    .str.replace("PLN", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
)
messy_df["price"] = pd.to_numeric(messy_df["price"], errors="coerce")

# Convert numeric and date columns to their correct dtypes.
messy_df["quantity"] = pd.to_numeric(messy_df["quantity"], errors="coerce")
messy_df["order_date"] = pd.to_datetime(
    messy_df["order_date"],
    format="%d.%m.%Y",
    errors="coerce"
)

# Remove duplicate rows.
messy_df = messy_df.drop_duplicates().reset_index(drop=True)

print("=== Clean DataFrame ===")
print(messy_df)

print("\n=== Dtypes ===")
print(messy_df.dtypes)

print("\n=== Missing values ===")
print(messy_df.isna().sum())

print("\n=== Number of duplicates ===")
print(messy_df.duplicated().sum())

print("\n=== Parameters used ===")
print("sep=';' -> semicolon-separated fields")
print("skiprows=2 -> skips the two junk lines before the header")
print("na_values=['n/a', '-', 'brak', ''] -> treats all listed markers as missing")
print("keep_default_na=True -> also keeps pandas' standard NA markers")
print("format='%d.%m.%Y' -> parses dates in DD.MM.YYYY format")
print("drop_duplicates() -> removes duplicate records")
