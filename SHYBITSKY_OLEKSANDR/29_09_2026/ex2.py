from pathlib import Path
import pandas as pd


def main() -> None:
    data_dir = Path(".")
    csv_path = data_dir / "sales_pl.csv"

    sales_pl_df = pd.read_csv(
        csv_path,
        sep=";",
        decimal=",",
        encoding="utf-8",
    )

    column_mapping = {
        "data": "date",
        "produkt": "product",
        "kategoria": "category",
        "region": "region",
        "ilosc": "quantity",
        "cena_jednostkowa": "unit_price",
    }

    cleaned_df = sales_pl_df.rename(columns=column_mapping)

    cleaned_df = cleaned_df.assign(
        date=pd.to_datetime(cleaned_df["date"], format="%Y-%m-%d")
    )

    print("=== Cleaned DataFrame Types ===")
    print(cleaned_df.dtypes)

    print("\n=== First 5 rows ===")
    print(cleaned_df.head())


if __name__ == "__main__":
    main()