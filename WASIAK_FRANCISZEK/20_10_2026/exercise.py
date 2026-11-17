from pathlib import Path

import pandas as pd
import pytest


# Slides 17–19: reusable filter functions

def filter_below(df, column, value):
    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")

    return df[df[column] < value]


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

    return df.sort_values(by=column, ascending=False).head(n)


# Slide 22: report challenge

def report(df, **filters):
    """Apply all filters with AND logic. No filters selects all rows."""
    for column in filters:
        if column not in df.columns:
            raise ValueError(f"Unknown column: {column}")

    for column in ("quantity", "unit_price"):
        if column not in df.columns:
            raise ValueError(f"Unknown column: {column}")

    filtered = df

    for column, value in filters.items():
        filtered = filtered[filtered[column] == value]

    total_value = (
        filtered["quantity"] * filtered["unit_price"]
    ).sum()

    print(f"Matched rows: {len(filtered)} / {len(df)}")
    print(f"Total sales value: {total_value:.2f}")

    return filtered


# Slides 18–19: pytest tests

def test_filter_below():
    df = pd.DataFrame({"quantity": [3, 10, 12, 25]})

    result = filter_below(df, "quantity", 10)

    assert result["quantity"].tolist() == [3]


def test_filter_between():
    df = pd.DataFrame({"quantity": [4, 5, 12, 20, 21]})

    result = filter_between(df, "quantity", 5, 20)

    assert result["quantity"].tolist() == [5, 12, 20]


def test_filter_by_values():
    df = pd.DataFrame({
        "region": ["North", "South", "East", "West"]
    })

    result = filter_by_values(df, "region", ["North", "East"])

    assert result["region"].tolist() == ["North", "East"]


def test_top_n():
    df = pd.DataFrame({"quantity": [3, 25, 12, 40]})

    result = top_n(df, "quantity", 2)

    assert result["quantity"].tolist() == [40, 25]


@pytest.mark.parametrize(
    "function, args",
    [
        (filter_below, (10,)),
        (filter_between, (5, 20)),
        (filter_by_values, (["North"],)),
        (top_n, (2,)),
    ],
)
def test_unknown_column(function, args):
    df = pd.DataFrame({"quantity": [3, 12, 25]})

    with pytest.raises(ValueError, match="Unknown column: missing"):
        function(df, "missing", *args)


def main():
    csv_path = Path(__file__).with_name("data.csv")
    df = pd.read_csv(csv_path)

    # Slide 16: filter expressions

    # 1. Keep rows where quantity is above 10.
    print("\n1. Quantity above 10")
    print(df[df["quantity"] > 10])

    # 2. Keep all sales in the North region.
    print("\n2. All sales in the North region")
    print(df[df["region"] == "North"])

    # 3. Keep Electronics sales in the North.
    print("\n3. Electronics sold in the North")
    print(df[
        (df["category"] == "Electronics")
        & (df["region"] == "North")
    ])

    # 4. Keep unit prices from 400 to 1500, inclusive.
    print("\n4. Unit price from 400 to 1500 inclusive")
    print(df[df["unit_price"].between(400, 1500)])

    # 5. Exclude only Electronics sales in the South.
    print("\n5. Everything except Electronics in the South")
    print(df[~(
        (df["category"] == "Electronics")
        & (df["region"] == "South")
    )])

    # 6. Keep North or East sales with quantity from 5 to 20.
    print("\n6. North or East, quantity between 5 and 20")
    print(df[
        df["region"].isin(["North", "East"])
        & df["quantity"].between(5, 20)
    ])

    # Slides 17–19: use the reusable functions

    print("\n--- Unit price below 100 ---")
    print(filter_below(df, "unit_price", 100))

    print("\n--- Unit price between 400 and 1500 ---")
    print(filter_between(df, "unit_price", 400, 1500))

    print("\n--- Sales in North or East ---")
    print(filter_by_values(df, "region", ["North", "East"]))

    print("\n--- Top 3 unit prices ---")
    print(top_n(df, "unit_price", 3))

    # Slides 20–21: safe modification
    # Work on a copy so the report still uses the original data.
    modified_df = df.copy()

    # Unsafe chained assignment:
    # modified_df[modified_df["region"] == "West"]["quantity"] = 0
    #
    # It may target a temporary object instead of updating modified_df.
    # Use a single .loc operation to select and assign instead.

    modified_df.loc[
        modified_df["region"] == "West", "quantity"
    ] = 0

    modified_df.loc[:, "discounted"] = (
        modified_df["category"] == "Furniture"
    )

    print("\n--- Modified data ---")
    print(modified_df)

    # Slide 22: report with AND logic

    print("\n--- Report: Electronics sold in the North ---")
    result = report(df, region="North", category="Electronics")
    print(result)


if __name__ == "__main__":
    main()