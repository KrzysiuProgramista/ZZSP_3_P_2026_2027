import pandas as pd


def report(df, **filters):
    for column in filters:
        if column not in df.columns:
            raise ValueError(f"Unknown column: {column}")

    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        mask &= df[column] == value

    result = df[mask]
    total_value = (result["quantity"] * result["unit_price"]).sum()

    print(f"Matched rows: {len(result)} / {len(df)}")
    print(f"Total value: {total_value}")

    return result


if __name__ == "__main__":
    df = pd.read_csv("data.csv")
    print(report(df, region="North", category="Electronics"))