from pathlib import Path
import pandas as pd

def main():
    data_dir = Path(".")
    messy_path = data_dir / "messy.csv"

    clean_df = (
        pd.read_csv(
            messy_path,
            sep=";",
            skiprows=2,
            na_values=["n/a", "-", "brak"],
            encoding="utf-8",
        )
        .assign(
            price=lambda df: df["price"]
            .str.replace(" PLN", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float),
            quantity=lambda df: df["quantity"].astype("Int64"),
            order_date=lambda df: pd.to_datetime(df["order_date"], format="%d.%m.%Y"),
        )
        .drop_duplicates()
    )

    print("Cleaned DataFrame shape:", clean_df.shape)
    print("\nData Types:")
    print(clean_df.dtypes)
    print("\nFirst 10 rows:")
    print(clean_df)

if __name__ == "__main__":
    main()