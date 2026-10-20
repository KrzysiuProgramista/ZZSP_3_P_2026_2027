from pathlib import Path
import pandas as pd


def report(df, **filters):
    result = df
    for column, value in filters.items():
        if column not in df.columns:
            raise ValueError(f"Unknown column: {column}")
        result = result[result[column] == value]

    total = (result["quantity"] * result["unit_price"]).sum()
    print(f"Matched rows: {len(result)} / {len(df)}")
    print(f"Total value: {total}")
    return result


if __name__ == "__main__":
    df = pd.read_csv(Path(__file__).parent / "data.csv")
    print(report(df, region="North", category="Electronics"))
