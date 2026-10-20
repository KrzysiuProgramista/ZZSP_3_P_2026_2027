import pandas as pd


def _check_column(df, column):
    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")


def filter_between(df, column, low, high):
    _check_column(df, column)
    return df[df[column].between(low, high)]


def filter_by_values(df, column, values):
    _check_column(df, column)
    return df[df[column].isin(values)]


def top_n(df, column, n):
    _check_column(df, column)
    if n < 0:
        raise ValueError("n must be >= 0")
    return df.sort_values(column, ascending=False).head(n)


if __name__ == "__main__":
    df = pd.read_csv("data.csv")
    print(filter_between(df, "unit_price", 400, 1500))
    print(filter_by_values(df, "region", ["North", "East"]))
    print(top_n(df, "unit_price", 3))