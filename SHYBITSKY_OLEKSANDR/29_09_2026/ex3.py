from pathlib import Path
import pandas as pd


def inspect(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("DATA FRAME INSPECTION ROUTINE")
    print("=" * 60)

    print(f"\n1. SHAPE: {df.shape[0]} rows, {df.shape[1]} columns")

    print("\n2. COLUMNS AND DTYPES:")
    for col, dtype in df.dtypes.items():
        print(f"  - {col}: {dtype}")

    print("\n3. MISSING VALUES:")
    null_counts = df.isna().sum()
    null_pcts = (df.isna().mean() * 100).round(2)
    missing_info = pd.DataFrame(
        {"Missing Count": null_counts, "Missing %": null_pcts}
    )
    print(missing_info)

    dup_count = df.duplicated().sum()
    print(f"\n4. DUPLICATE ROWS: {dup_count}")

    num_cols = df.select_dtypes(include=["number"]).columns
    print("\n5. NUMERIC COLUMNS SUMMARY:")
    if len(num_cols) > 0:
        stats = []
        for col in num_cols:
            stats.append(
                {
                    "column": col,
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": round(df[col].mean(), 2),
                    "median": df[col].median(),
                }
            )
        stats_df = pd.DataFrame(stats).set_index("column")
        print(stats_df)
    else:
        print("  No numeric columns found.")

    obj_cols = df.select_dtypes(include=["object", "category"]).columns
    print("\n6. OBJECT/CATEGORICAL COLUMNS SUMMARY:")
    if len(obj_cols) > 0:
        for col in obj_cols:
            n_unique = df[col].nunique()
            top3 = df[col].value_counts().head(3).to_dict()
            top3_str = ", ".join([f"'{k}': {v}" for k, v in top3.items()])
            print(
                f"  - {col}: {n_unique} unique values | Top 3: [{top3_str}]"
            )
    else:
        print("  No object/categorical columns found.")

    print("=" * 60 + "\n")


def main() -> None:
    data_dir = Path(".")

    print("\n>>> Testing inspect() on sales.csv <<<")
    sales_df = pd.read_csv(data_dir / "sales.csv", encoding="utf-8")
    inspect(sales_df)

    print("\n>>> Testing inspect() on sales_pl.csv <<<")
    sales_pl_df = pd.read_csv(
        data_dir / "sales_pl.csv",
        sep=";",
        decimal=",",
        encoding="utf-8",
    )
    inspect(sales_pl_df)


if __name__ == "__main__":
    main()