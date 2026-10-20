import pandas as pd

# Exercise 8: The messy import
# - sep=";": file uses semicolons
# - skiprows=2: skips the 2 junk lines before the header
# - decimal=",": parses Polish decimal commas correctly (when the string represents a pure number)
# - na_values=["n/a", "-", "brak"]: catches missing data encoded as strings
df_messy = pd.read_csv(
    "messy.csv",
    sep=";",
    skiprows=2,
    decimal=",",
    na_values=["n/a", "-", "brak"]
)

# Fix the price column: it has " PLN" and spaces preventing it from being parsed as a float
# We use .str to do vectorized string replacements, then convert to float.
if df_messy["price"].dtype == "object":
    df_messy["price"] = (
        df_messy["price"]
        .str.replace(" PLN", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

# Fix the date column: convert to standard pandas datetime using format DD.MM.YYYY
df_messy["order_date"] = pd.to_datetime(df_messy["order_date"], format="%d.%m.%Y")

# Drop duplicates
df_messy = df_messy.drop_duplicates()

print("--- Cleaned Messy DataFrame ---")
print(df_messy)
print("\n--- Dtypes ---")
print(df_messy.dtypes)
