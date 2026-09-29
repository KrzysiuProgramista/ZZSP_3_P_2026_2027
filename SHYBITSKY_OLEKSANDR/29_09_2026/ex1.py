from pathlib import Path
import pandas as pd


def main() -> None:
    data_dir = Path(".")
    csv_path = data_dir / "sales.csv"

    sales_df = pd.read_csv(csv_path, encoding="utf-8")

    print("=== First 5 rows ===")
    print(sales_df.head(5))

    print("\n=== Shape ===")
    print(sales_df.shape)

    print("\n=== Data types ===")
    print(sales_df.dtypes)

    print("\n=== Column names ===")
    print(sales_df.columns.tolist())

    print("\n=== Memory usage (deep) ===")
    sales_df.info(memory_usage="deep")


if __name__ == "__main__":
    main()