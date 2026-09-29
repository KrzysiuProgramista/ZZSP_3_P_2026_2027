from pathlib import Path
import json
import time

import pandas as pd

HERE = Path(__file__).resolve().parent


def inspect(df: pd.DataFrame) -> None:
    """Print a reusable first-pass inspection of a DataFrame."""
    print(f"Shape: {df.shape}")
    print("\nColumns and dtypes:")
    for column, dtype in df.dtypes.items():
        print(f"  {column}: {dtype}")

    print("\nMissing values:")
    for column in df.columns:
        count = df[column].isna().sum()
        percent = 100 * count / len(df) if len(df) else 0
        print(f"  {column}: {count} ({percent:.2f}%)")

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    print("\nNumeric columns:")
    numeric_columns = df.select_dtypes(include="number").columns
    if len(numeric_columns) == 0:
        print("  No numeric columns")
    for column in numeric_columns:
        values = df[column]
        print(
            f"  {column}: min={values.min()}, max={values.max()}, "
            f"mean={values.mean():.2f}, median={values.median()}"
        )

    print("\nText/object columns:")
    text_columns = df.select_dtypes(include=["object", "string"]).columns
    if len(text_columns) == 0:
        print("  No text/object columns")
    for column in text_columns:
        values = df[column]
        try:
            print(f"  {column}: {values.nunique(dropna=True)} unique values")
            print(values.value_counts(dropna=True).head(3).to_string())
        except TypeError:
            print(f"  {column}: contains unhashable values such as lists/dictionaries")


def price_to_float(value: str) -> float | None:
    """Convert '3 500,00 PLN' to 3500.0; return None for missing markers."""
    if value.strip().lower() in {"", "n/a", "-", "brak"}:
        return None
    return float(value.replace("PLN", "").replace(" ", "").replace(",", "."))


def main() -> None:
    print("=" * 60)
    print("EXERCISE 1 — BASIC CSV READING")
    print("=" * 60)
    sales_df = pd.read_csv(HERE / "sales.csv")
    print("\nFirst 5 rows:")
    print(sales_df.head())
    print("\nShape:", sales_df.shape)
    print("\nDtypes:")
    print(sales_df.dtypes)
    print("\nColumn names:", sales_df.columns.tolist())
    print("\nMemory usage:")
    sales_df.info(memory_usage="deep")

    print("\n" + "=" * 60)
    print("EXERCISE 2 — POLISH CSV")
    print("=" * 60)
    sales_pl_df = pd.read_csv(HERE / "sales_pl.csv", sep=";", decimal=",")
    sales_pl_df = sales_pl_df.rename(columns={
        "data": "date",
        "produkt": "product",
        "kategoria": "category",
        "region": "region",
        "ilosc": "quantity",
        "cena_jednostkowa": "unit_price",
    })
    print("\nRenamed data:")
    print(sales_pl_df)
    print("\nDtypes:")
    print(sales_pl_df.dtypes)
    assert pd.api.types.is_numeric_dtype(sales_pl_df["quantity"])
    assert pd.api.types.is_numeric_dtype(sales_pl_df["unit_price"])
    print("quantity and unit_price are numeric")

    print("\n" + "=" * 60)
    print("EXERCISE 3 — INSPECT sales.csv")
    print("=" * 60)
    inspect(sales_df)
    print("\n" + "=" * 60)
    print("EXERCISE 3 — INSPECT sales_pl.csv")
    print("=" * 60)
    inspect(sales_pl_df)

    print("\n" + "=" * 60)
    print("EXERCISE 4 — JSON")
    print("=" * 60)
    products_df = pd.read_json(HERE / "products.json")
    print("\nOriginal DataFrame:")
    print(products_df)
    with (HERE / "products.json").open(encoding="utf-8") as f:
        flattened_df = pd.json_normalize(json.load(f))
    print("\nFlattened DataFrame:")
    print(flattened_df)
    print("\nOriginal columns:", products_df.columns.tolist())
    print("Flattened columns:", flattened_df.columns.tolist())
    print("Original supplier cell:", products_df.loc[0, "supplier"])
    print("Flattened supplier name:", flattened_df.loc[0, "supplier.name"])

    print("\n" + "=" * 60)
    print("EXERCISE 5 — WRITING AND READING FILES")
    print("=" * 60)
    cleaned_sales_df = sales_pl_df.copy()
    cleaned_sales_df["date"] = pd.to_datetime(cleaned_sales_df["date"])
    csv_file = HERE / "sales_clean.csv"
    json_file = HERE / "sales_clean.json"
    excel_file = HERE / "sales_clean.xlsx"
    cleaned_sales_df.to_csv(csv_file, index=False)
    cleaned_sales_df.to_json(
        json_file, orient="records", date_format="iso", indent=2, force_ascii=False
    )
    cleaned_sales_df.to_excel(excel_file, index=False)
    print("\nJSON file contents:")
    print(json_file.read_text(encoding="utf-8"))

    restored = (
        ("CSV", pd.read_csv(csv_file, parse_dates=["date"])),
        ("JSON", pd.read_json(json_file, orient="records", convert_dates=["date"])),
        ("Excel", pd.read_excel(excel_file, parse_dates=["date"])),
    )
    for file_type, loaded_df in restored:
        pd.testing.assert_frame_equal(
            cleaned_sales_df, loaded_df[cleaned_sales_df.columns], check_dtype=True
        )
        print(f"{file_type}: data matches cleaned_sales_df")

    print("\n" + "=" * 60)
    print("EXERCISE 6 — ONLY WHAT YOU NEED")
    print("=" * 60)
    # sales.csv has no amount field; derive one, then make a full file to read.
    sales_with_amount = sales_df.copy()
    sales_with_amount["amount"] = (
        sales_with_amount["quantity"] * sales_with_amount["unit_price"]
    )
    amount_file = HERE / "sales_with_amount.csv"
    sales_with_amount.to_csv(amount_file, index=False)
    first_ten = pd.read_csv(
        amount_file, usecols=["date", "product", "amount"], nrows=10
    )
    print("\nFirst 10 rows, selected columns:")
    print(first_ten)

    repeats = 100
    start = time.perf_counter()
    for _ in range(repeats):
        pd.read_csv(amount_file)
    full_seconds = (time.perf_counter() - start) / repeats
    start = time.perf_counter()
    for _ in range(repeats):
        pd.read_csv(amount_file, usecols=["date", "product", "amount"])
    selected_seconds = (time.perf_counter() - start) / repeats
    print(f"\nAverage full read over {repeats} runs: {full_seconds:.6f} seconds")
    print(f"Average selected-column read: {selected_seconds:.6f} seconds")
    print("This 15-row file is too small for a meaningful speed comparison.")

    print("\n" + "=" * 60)
    print("EXERCISE 7 — TITANIC DATASET")
    print("=" * 60)
    titanic_path = HERE / "Titanic-Dataset.csv"
    if titanic_path.exists():
        titanic_df = pd.read_csv(titanic_path)
        print("\nTitanic inspection:")
        inspect(titanic_df)
        print("\nFive questions this dataset can answer:")
        print("1. What percentage of recorded passengers survived?")
        print("2. How did survival rates vary by sex?")
        print("3. How did survival rates vary by passenger class?")
        print("4. How did survival rates vary by age?")
        print("5. How did survival rates vary by embarkation port?")
        print("\nAnswers to the two easiest questions:")
        print(f"1. Overall survival: {titanic_df['Survived'].mean() * 100:.2f}%")
        print("2. Survival by sex (%):")
        print((titanic_df.groupby("Sex")["Survived"].mean() * 100).round(2))
        print("\nTwo questions this dataset cannot answer:")
        print("1. What was each passenger's occupation? Missing: occupation records.")
        print("2. Which lifeboat did each passenger board? Missing: lifeboat assignments.")
    else:
        print("Titanic-Dataset.csv not found beside exercises.py.")
        print("Download and extract the Kaggle dataset, then rerun this script.")
        print("The questions and answers above require the actual CSV; no results are invented.")

    print("\n" + "=" * 60)
    print("EXERCISE 8 — MESSY IMPORT")
    print("=" * 60)
    messy_df = pd.read_csv(
        HERE / "messy.csv",
        sep=";",                         # Semicolon-delimited file.
        skiprows=2,                      # Two export-info lines precede the header.
        na_values=["n/a", "-", "brak", ""],  # Missing-value markers.
        parse_dates=["order_date"],      # Parse dates during import.
        date_format="%d.%m.%Y",         # Day.month.year format.
        converters={"price": price_to_float},  # Strip PLN and convert comma decimals.
        dtype={"id": "Int64", "name": "string", "quantity": "Int64", "notes": "string"},
    ).drop_duplicates(ignore_index=True)  # Remove exact duplicate rows.
    print("\nCleaned data:")
    print(messy_df)
    print("\nDtypes:")
    print(messy_df.dtypes)
    print("\nDuplicate rows:", messy_df.duplicated().sum())
    print("\nMissing values:")
    print(messy_df.isna().sum())
    print("\nParameters: sep=delimiter; skiprows=metadata; na_values=missing markers;")
    print("parse_dates/date_format=DD.MM.YYYY dates; converters=PLN prices;")
    print("dtype=nullable integers and strings; drop_duplicates=unique rows.")


if __name__ == "__main__":
    main()