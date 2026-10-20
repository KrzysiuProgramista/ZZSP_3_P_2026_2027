from pathlib import Path
import pandas as pd


def main() -> None:
    data_dir = Path(".")

    raw_df = pd.read_csv(
        data_dir / "sales_pl.csv",
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
    sales_clean = raw_df.rename(columns=column_mapping)

    clean_csv_path = data_dir / "sales_clean.csv"
    clean_json_path = data_dir / "sales_clean.json"
    clean_excel_path = data_dir / "sales_clean.xlsx"

    sales_clean.to_csv(clean_csv_path, index=False, encoding="utf-8")

    sales_clean.to_json(
        clean_json_path, orient="records", force_ascii=False, indent=2
    )

    sales_clean.to_excel(
        clean_excel_path, index=False, engine="openpyxl", sheet_name="SalesData"
    )

    read_csv_df = pd.read_csv(clean_csv_path, encoding="utf-8")
    read_json_df = pd.read_json(clean_json_path, orient="records", encoding="utf-8")
    read_excel_df = pd.read_excel(
        clean_excel_path, sheet_name="SalesData", engine="openpyxl"
    )

    print("=== Verification ===")
    print("CSV matches shape:", read_csv_df.shape == sales_clean.shape)
    print("JSON matches shape:", read_json_df.shape == sales_clean.shape)
    print("Excel matches shape:", read_excel_df.shape == sales_clean.shape)


if __name__ == "__main__":
    main()