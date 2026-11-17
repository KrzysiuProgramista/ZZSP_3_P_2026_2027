import pandas as pd

df = pd.read_csv("data.csv")


# ---------- Selecting (slides 6, 8, 9, 10) ----------
def selecting_exercises(df):
    all_but_region = df.drop(columns=["region"])
    loc_rows = df.loc[0:4, ["product", "quantity"]]          # loc: stop included -> 5 rows
    iloc_rows = df.iloc[0:5, [1, 4]]                          # iloc: stop excluded -> 5 rows
    by_product = df.set_index("product")
    laptops = by_product.loc["Laptop"]                        # 4 Laptop sales -> DataFrame (not Series)
    return all_but_region, loc_rows, iloc_rows, laptops


# ---------- Slide 8 predictions ----------
# df.iloc[2:6] -> 4 rows | df.loc[2:5] -> 4 rows | df.iloc[2:5] -> 3 rows | df.loc[2:5] -> 4 rows


# ---------- Practice 1 (slide 16) ----------
p1 = {
    1: df[df["quantity"] > 10],
    2: df[df["region"] == "North"],
    3: df[(df["category"] == "Electronics") & (df["region"] == "North")],
    4: df[df["unit_price"].between(400, 1500)],
    5: df[~((df["category"] == "Electronics") & (df["region"] == "South"))],
    6: df[df["region"].isin(["North", "East"]) & df["quantity"].between(5, 20)],
}

# ---------- query() rewrites (slide 15) ----------
q1 = df.query("quantity > 10")
q3 = df.query("category == 'Electronics' and region == 'North'")
q6 = df.query("region in ['North', 'East'] and 5 <= quantity <= 20")


# ---------- Practice 2 (slides 17-19) ----------
def _check_column(df, column):
    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")


def filter_below(df, column, value):
    _check_column(df, column)
    return df[df[column] < value]


def filter_between(df, column, low, high):
    _check_column(df, column)
    return df[df[column].between(low, high)]


def filter_by_values(df, column, values):
    _check_column(df, column)
    return df[df[column].isin(values)]


def top_n(df, column, n):
    _check_column(df, column)
    return df.sort_values(column, ascending=False).head(n)


# ---------- Modifying safely (slides 20-21) ----------
def modify_example(df):
    out = df.copy()
    out.loc[out["region"] == "West", "quantity"] = 0
    out.loc[:, "discounted"] = out["category"] == "Furniture"
    # Unsafe: df[df["region"] == "West"]["quantity"] = 0
    # The first [] returns a temporary copy, so the assignment hits the copy, not df.
    return out


# ---------- Challenge (slide 22) ----------
def report(df, **filters):
    for column in filters:
        _check_column(df, column)
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        mask &= df[column] == value
    result = df[mask]
    total_value = (result["quantity"] * result["unit_price"]).sum()
    print(f"Matched rows: {len(result)} / {len(df)}")
    print(f"Total value: {total_value:.2f}")
    return result  # report(df) with no filters returns all rows


# ---------- Exit ticket (slide 24) ----------
# 1. df["product"] -> Series; df[["product"]] -> one-column DataFrame.
# 2. loc slices by label and includes the stop; iloc slices by position and excludes it.
# 3. Python's `and` needs one truth value; a Series holds many. & works element-wise.
# 4. query() is more readable for simple conditions, e.g. "quantity > 10 and region == 'North'".
# 5. One .loc call selects and assigns on the original df; chained indexing may assign to a temporary copy.
