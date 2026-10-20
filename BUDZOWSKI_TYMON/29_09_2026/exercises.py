"""01 - Reading and writing files with pandas.

Worked solutions. See README.md for the task descriptions.
Run with:  python exercises.py
"""

import pandas as pd


def header(text):
    print(f"\n{'=' * 70}\n{text}\n{'=' * 70}")


# --- Exercise 1: basic CSV reading ---------------------------------------

def exercise_1():
    header("EXERCISE 1 - sales.csv")
    sales_df = pd.read_csv("sales.csv")

    print("First 5 rows:")
    print(sales_df.head())
    print(f"\nShape: {sales_df.shape}  ({sales_df.shape[0]} rows, "
          f"{sales_df.shape[1]} columns)")
    print("\nDtypes:")
    print(sales_df.dtypes)
    print(f"\nColumns: {list(sales_df.columns)}")

    print("\nMemory usage:")
    sales_df.info(memory_usage="deep")

    # `date` came in as text, not a date. Two ways to fix it:
    #   pd.read_csv("sales.csv", parse_dates=["date"])
    #   sales_df["date"] = pd.to_datetime(sales_df["date"])
    sales_df["date"] = pd.to_datetime(sales_df["date"])
    print(f"\nAfter to_datetime, date is: {sales_df['date'].dtype}")

    return sales_df


# --- Exercise 2: the awkward file ----------------------------------------

def exercise_2():
    header("EXERCISE 2 - sales_pl.csv")

    # sep=";"      -> semicolon separated
    # decimal=","  -> "3500,00" is a number, not text
    # parse_dates  -> the date column becomes datetime64 straight away
    pl_df = pd.read_csv(
        "sales_pl.csv",
        sep=";",
        decimal=",",
        parse_dates=["data"],
    )

    print("Dtypes as read (Polish columns):")
    print(pl_df.dtypes)

    pl_df = pl_df.rename(columns={
        "data": "date",
        "produkt": "product",
        "kategoria": "category",
        "region": "region",
        "ilosc": "quantity",
        "cena_jednostkowa": "unit_price",
    })

    print("\nAfter rename:")
    print(pl_df.head())
    print("\nDtypes:")
    print(pl_df.dtypes)

    # The check the exercise asks for: nothing numeric left as text.
    numeric = ["quantity", "unit_price"]
    bad = [c for c in numeric if not pd.api.types.is_numeric_dtype(pl_df[c])]
    print(f"\nNumeric columns still stored as text: {bad or 'none'}")

    return pl_df


# --- Exercise 3: first-pass inspection -----------------------------------

def text_columns(df):
    """Text-ish columns, on both pandas 2 (object) and pandas 3 (str)."""
    return df.select_dtypes(
        exclude=["number", "datetime", "timedelta", "bool"]
    ).columns


def inspect(df, name="DataFrame"):
    """Print a first-pass summary of any DataFrame."""
    print(f"\n--- inspect({name}) ---")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    print("\nColumns and dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"  {col:<20} {dtype}")

    print("\nMissing values:")
    missing = df.isna().sum()
    pct = missing / len(df) * 100
    for col in df.columns:
        print(f"  {col:<20} {missing[col]:>4}  ({pct[col]:5.1f}%)")

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    numeric = df.select_dtypes(include="number")
    if not numeric.empty:
        print("\nNumeric columns:")
        print(f"  {'column':<20}{'min':>12}{'max':>12}"
              f"{'mean':>12}{'median':>12}")
        for col in numeric.columns:
            s = numeric[col]
            print(f"  {col:<20}{s.min():>12.2f}{s.max():>12.2f}"
                  f"{s.mean():>12.2f}{s.median():>12.2f}")

    text = text_columns(df)
    if len(text):
        print("\nText columns:")
        for col in text:
            top = df[col].value_counts().head(3)
            top_str = ", ".join(f"{v} ({n})" for v, n in top.items())
            print(f"  {col:<20} {df[col].nunique()} unique | top 3: {top_str}")


# --- Exercise 4: reading JSON --------------------------------------------

def exercise_4():
    header("EXERCISE 4 - products.json")

    raw = pd.read_json("products.json")
    print("pd.read_json - nested objects stay as Python dicts in the cell:")
    print(raw)
    print(f"\nType of one supplier cell: {type(raw.loc[0, 'supplier'])}")
    print("Dtypes:")
    print(raw.dtypes)

    flat = pd.json_normalize(pd.read_json("products.json").to_dict("records"))
    print("\npd.json_normalize - the dict is split into its own columns:")
    print(flat)
    print(f"\nColumns: {list(flat.columns)}")

    # `tags` is a list, not a dict, so json_normalize leaves it alone.
    # To get one row per tag:
    print("\nExploded tags (one row per tag):")
    print(flat.explode("tags")[["id", "name", "tags"]].head(6))

    return raw, flat


# --- Exercise 5: writing files -------------------------------------------

def exercise_5(df):
    header("EXERCISE 5 - writing files")

    df.to_csv("sales_clean.csv", index=False)
    # date_format="iso" keeps the dates readable; the default writes them
    # as milliseconds since 1970.
    df.to_json("sales_clean.json", orient="records", indent=2,
               date_format="iso")
    df.to_excel("sales_clean.xlsx", index=False)
    print("Wrote sales_clean.csv, sales_clean.json, sales_clean.xlsx")

    print("\nFirst lines of sales_clean.json:")
    with open("sales_clean.json") as f:
        print("".join(f.readlines()[:8]).rstrip())

    back_csv = pd.read_csv("sales_clean.csv", parse_dates=["date"])
    back_json = pd.read_json("sales_clean.json", orient="records")
    back_xlsx = pd.read_excel("sales_clean.xlsx")

    print("\nRound-trip check with df.equals():")
    for label, other in [("csv", back_csv), ("json", back_json),
                         ("xlsx", back_xlsx)]:
        print(f"  {label:<5} {df.equals(other)}")

    # If one says False, this is how you find out where it differs:
    print("\nDtypes side by side:")
    print(pd.DataFrame({
        "original": df.dtypes,
        "csv": back_csv.dtypes,
        "json": back_json.dtypes,
        "xlsx": back_xlsx.dtypes,
    }))
    print(
        "\nThe values are identical; only unit_price changed type. Every\n"
        "price here happens to be a whole number, so JSON and Excel store\n"
        "them as integers and pandas reads them back as int64. CSV survives\n"
        "because '3500.0' still looks like a float in the text. Fix it on\n"
        "read with astype, or dtype={'unit_price': float}."
    )


if __name__ == "__main__":
    sales_df = exercise_1()
    pl_df = exercise_2()

    header("EXERCISE 3 - inspect()")
    inspect(sales_df, "sales_df")
    inspect(pl_df, "pl_df")

    exercise_4()
    exercise_5(sales_df)
