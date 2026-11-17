import pandas as pd
import io

csv_data = """Date,product,category,region,quantity,unit_price
2026-01-05,Laptop,Electronics,North,3,3500.00
2026-01-07,Mouse,Electronics,North,25,45.00
2026-01-12,Desk,Furniture,South,5,890.00
2026-01-15,Laptop,Electronics,South,2,3500.00
2026-01-19,Chair,Furniture,North,12,450.00
2026-02-02,Monitor,Electronics,East,8,1200.00
2026-02-08,Desk,Furniture,East,3,890.00
2026-02-14,Mouse,Electronics,West,40,45.00
2026-02-21,Laptop,Electronics,West,1,3500.00
2026-03-03,Chair,Furniture,South,20,450.00
2026-03-11,Monitor,Electronics,North,4,1200.00
2026-03-18,Keyboard,Electronics,East,15,199.00
2026-03-25,Desk,Furniture,West,7,890.00
2026-04-02,Laptop,Electronics,North,5,3500.00
2026-04-09,Chair,Furniture,East,9,450.00
2026-04-16,Keyboard,Electronics,South,30,199.00
2026-04-23,Monitor,Electronics,West,6,1200.00
2026-05-04,Desk,Furniture,North,2,890.00"""

df = pd.read_csv(io.StringIO(csv_data))

print("1. Quantity above 10:")
print(df[df['quantity'] > 10])

print("\n2. All sales in the North region:")
print(df[df['region'] == 'North'])

print("\n3. Electronics sold in the North:")
print(df[(df['category'] == 'Electronics') & (df['region'] == 'North')])

print("\n4. Unit price from 400 to 1,500 inclusive:")
print(df[df['unit_price'].between(400, 1500)])

print("\n5. Everything except Electronics in the South:")
print(df[~((df['category'] == 'Electronics') & (df['region'] == 'South'))])

print("\n6. Sales in North or East; quantity between 5 and 20:")
print(df[df['region'].isin(['North', 'East']) & df['quantity'].between(5, 20)])

# Practice 2: reusable filter toolkit
import pytest
from pandas.testing import assert_frame_equal


def validate_column(df, column):
    if column not in df.columns:
        raise ValueError(f"Nieznana kolumna: {column}")


def filter_between(df, column, low, high):
    validate_column(df, column)
    return df.loc[df[column].between(low, high, inclusive="both")].copy()


def filter_by_values(df, column, values):
    validate_column(df, column)
    return df.loc[df[column].isin(values)].copy()


def top_n(df, column, n):
    validate_column(df, column)
    return df.sort_values(by=column, ascending=False).head(n).copy()


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "product": ["Laptop", "Mouse", "Desk", "Chair"],
        "quantity": [3, 25, 5, 12],
        "region": ["North", "North", "South", "East"],
    })


def test_filter_between(sample_df):
    result = filter_between(sample_df, "quantity", 5, 12)
    assert_frame_equal(result, sample_df.iloc[[2, 3]])


def test_filter_by_values(sample_df):
    result = filter_by_values(sample_df, "region", ["North", "East"])
    assert_frame_equal(result, sample_df.iloc[[0, 1, 3]])


def test_top_n(sample_df):
    result = top_n(sample_df, "quantity", 2)
    assert_frame_equal(result, sample_df.iloc[[1, 3]])


@pytest.mark.parametrize("function,args", [
    (filter_between, (5, 12)),
    (filter_by_values, (["North"],)),
    (top_n, (2,)),
])
def test_unknown_column(sample_df, function, args):
    with pytest.raises(ValueError, match="Nieznana kolumna"):
        function(sample_df, "missing_column", *args)


if __name__ == "__main__":
    print("\nPractice 2 — quantity from 5 to 12:")
    print(filter_between(df, "quantity", 5, 12))

    print("\nPractice 2 — North or East:")
    print(filter_by_values(df, "region", ["North", "East"]))

    print("\nPractice 2 — top 3 by quantity:")
    print(top_n(df, "quantity", 3))
