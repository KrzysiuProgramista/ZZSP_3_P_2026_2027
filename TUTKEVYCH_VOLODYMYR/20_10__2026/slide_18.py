from pathlib import Path
import pandas as pd
import pytest

df = pd.read_csv(Path(__file__).parent / "data.csv")


def filter_between(df, column, low, high):
    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")
    return df[df[column].between(low, high)]


def filter_by_values(df, column, values):
    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")
    return df[df[column].isin(values)]


def top_n(df, column, n):
    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")
    return df.sort_values(column, ascending=False).head(n)


def test_filter_between():
    result = filter_between(df, "quantity", 5, 20)
    assert result["quantity"].between(5, 20).all()


def test_filter_by_values():
    result = filter_by_values(df, "region", ["North", "East"])
    assert result["region"].isin(["North", "East"]).all()


def test_top_n():
    result = top_n(df, "quantity", 3)
    assert list(result["quantity"]) == [40, 30, 25]


def test_unknown_column():
    with pytest.raises(ValueError):
        filter_between(df, "price", 1, 2)
