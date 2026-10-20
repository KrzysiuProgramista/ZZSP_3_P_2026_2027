import json
import os
import time
import pandas as pd
import numpy as np

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


# ---------------------------------------------------------------- Exercise 1
print("\n===== EXERCISE 1: basic CSV reading =====")
sales_df = pd.read_csv("sales.csv")

print(sales_df.head(5))
print("shape:", sales_df.shape)
print(sales_df.dtypes)

print("columns:", list(sales_df.columns))

sales_df.info(memory_usage="deep")


# ---------------------------------------------------------------- Exercise 2
print("\n===== EXERCISE 2: the awkward file =====")
# sep=";"     -> fields are split on semicolons
# decimal="," -> "9,99" becomes the float 9.99
# If you get a UnicodeDecodeError, add encoding="cp1250" (or "utf-8-sig").
sales_pl = pd.read_csv("sales_pl.csv", sep=";", decimal=",", encoding="utf-8")
print("Original columns:", list(sales_pl.columns))

# Fill in / adjust this dict to match the Polish headers in YOUR file.
# Columns not listed are simply left unchanged.
PL_TO_EN = {
    "data": "date",
    "region": "region",
    "produkt": "product",
    "ilość": "quantity",
    "cena_jednostkowa": "unit_price",
    "kategoria": "category",
}
sales_pl = sales_pl.rename(columns=PL_TO_EN)

# Optional: real dates instead of strings
if "date" in sales_pl.columns:
    sales_pl["date"] = pd.to_datetime(sales_pl["date"])

print(sales_pl.dtypes)

# Any 'object' column that should be a number? (thousands separators, stray
# text, etc.) This lists suspicious ones:
for col in sales_pl.select_dtypes(include=["object", "string"]):
    converted = pd.to_numeric(
        sales_pl[col].astype(str).str.replace(",", ".").str.replace(" ", ""),
        errors="coerce",
    )
    if converted.notna().all():
        print(f"WARNING: '{col}' looks numeric but is object -> fix it")
# If a column is wrongly object, e.g. "1 234,50":
#   read_csv(..., thousands=" ")  or  .str.replace(...).astype(float)


# ---------------------------------------------------------------- Exercise 3
def inspect(df):
    """First-pass inspection routine for any DataFrame."""
    print("=" * 60)
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    print("\nColumns and dtypes:")
    for col, dt in df.dtypes.items():
        print(f"  {col:<25} {dt}")

    print("\nMissing values:")
    missing = df.isna().sum()
    pct = (missing / len(df) * 100).round(2) if len(df) else missing * 0
    print(pd.DataFrame({"missing": missing, "percent": pct}).to_string())

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    num = df.select_dtypes("number")
    if not num.empty:
        print("\nNumeric columns:")
        print(num.agg(["min", "max", "mean", "median"]).T.to_string())

    obj = df.select_dtypes(include=["object", "string"])
    if not obj.empty:
        print("\nText columns:")
        for col in obj:
            top3 = obj[col].value_counts().head(3).to_dict()
            print(f"  {col}: {obj[col].nunique()} unique, top 3: {top3}")
    print("=" * 60)


print("\n===== EXERCISE 3: inspect() =====")
inspect(sales_df)
inspect(sales_pl)


# ---------------------------------------------------------------- Exercise 4
print("\n===== EXERCISE 4: JSON =====")
products = pd.read_json("products.json")
print(products)
print(products.dtypes)
print("Type of a nested cell:", type(products.iloc[0, -1]))  # dict

with open("products.json", encoding="utf-8") as f:
    raw = json.load(f)
# if the records sit under a key, e.g. {"products": [...]}, pick that list
if isinstance(raw, dict):
    raw = next(v for v in raw.values() if isinstance(v, list))

flat = pd.json_normalize(raw)          # nested keys -> "supplier.name" etc.
print(flat)
print(flat.columns.tolist())

print("\nComparison:")
print("nested :", products.shape, list(products.columns))
print("flat   :", flat.shape, list(flat.columns))
# json_normalize(raw, sep="_") gives supplier_name instead of supplier.name


# ---------------------------------------------------------------- Exercise 5
print("\n===== EXERCISE 5: writing files =====")
# "Cleaned" here = duplicates dropped, dates parsed.
clean = sales_df.drop_duplicates().reset_index(drop=True)
if "date" in clean.columns:
    clean["date"] = pd.to_datetime(clean["date"])

clean.to_csv("sales_clean.csv", index=False)
clean.to_json("sales_clean.json", orient="records", indent=2, date_format="iso")
clean.to_excel("sales_clean.xlsx", index=False)   # needs: pip install openpyxl

print(open("sales_clean.json", encoding="utf-8").read()[:400])

date_cols = ["date"] if "date" in clean.columns else []
back_csv = pd.read_csv("sales_clean.csv", parse_dates=date_cols)
back_json = pd.read_json("sales_clean.json", orient="records")
back_xlsx = pd.read_excel("sales_clean.xlsx")

for name, back in [("CSV", back_csv), ("JSON", back_json), ("Excel", back_xlsx)]:
    try:
        pd.testing.assert_frame_equal(clean, back, check_dtype=False)
        print(f"{name}: identical data")
    except AssertionError as e:
        print(f"{name}: DIFFERENT -> {str(e)[:200]}")

def inspect(df):
    """First-pass inspection routine for any DataFrame."""
    print("=" * 60)
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    print("\nColumns and dtypes:")
    for col, dt in df.dtypes.items():
        print(f"  {col:<25} {dt}")

    print("\nMissing values:")
    missing = df.isna().sum()
    pct = (missing / len(df) * 100).round(2) if len(df) else missing * 0
    print(pd.DataFrame({"missing": missing, "percent": pct}).to_string())

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    num = df.select_dtypes("number")
    if not num.empty:
        print("\nNumeric columns:")
        print(num.agg(["min", "max", "mean", "median"]).T.to_string())

    obj = df.select_dtypes(include=["object", "string"])
    if not obj.empty:
        print("\nText columns:")
        for col in obj:
            top3 = obj[col].value_counts().head(3).to_dict()
            print(f"  {col}: {obj[col].nunique()} unique, top 3: {top3}")
    print("=" * 60)


# 1. only three columns (column names must exist in your file)
cols = ["date", "product", "amount"]
part = pd.read_csv("sales_big.csv", usecols=cols)
print(part.head(), "\n", part.shape)

# 2. only the first 10 rows
first10 = pd.read_csv("sales.csv", nrows=10)
print(first10.shape)

# 3. timing. In a notebook you would write:
#      %timeit pd.read_csv("sales.csv")
#      %timeit pd.read_csv("sales.csv", usecols=cols)
#      %timeit pd.read_csv("sales.csv", nrows=10)
def bench(path, label, repeats=5, **kwargs):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        pd.read_csv(path, **kwargs)
        times.append(time.perf_counter() - t0)
    print(f"  {label:<22} best of {repeats}: {min(times) * 1000:8.2f} ms")


def run_bench(path):
    print(f"\nTiming on {path} ({os.path.getsize(path) / 1e6:.2f} MB)")
    bench(path, "full file")
    bench(path, "usecols (3 cols)", usecols=cols)
    bench(path, "nrows=10", nrows=10)


run_bench("sales_big.csv")

# Your real file may be small, so the differences are tiny (milliseconds).
# To see the effect, build a 1-million-row file and time that too:
if not os.path.exists("sales_big.csv"):
    rng = np.random.default_rng(0)
    n = 1_000_000
    pd.DataFrame({
        "order_id": np.arange(n),
        "date": pd.Timestamp("2020-01-01") + pd.to_timedelta(rng.integers(0, 1500, n), "D"),
        "region": rng.choice(["North", "South", "East", "West"], n),
        "product": rng.choice(["Widget", "Gadget", "Doohickey"], n),
        "amount": rng.uniform(1, 500, n).round(2),
        "comment": rng.choice(["ok", "late delivery", "returned", "gift wrap"], n),
    }).to_csv("sales_big.csv", index=False)
run_bench("sales_big.csv")

# ---------------------------------------------------------------- Exercise 7
print("\n===== EXERCISE 7: Titanic =====")
# Kaggle needs a login to download, so save Titanic-Dataset.csv from
# https://www.kaggle.com/datasets/yasserh/titanic-dataset into this folder.
path = next(p for p in ["Titanic-Dataset.csv", "titanic.csv"] if os.path.exists(p))
titanic = pd.read_csv(path)
inspect(titanic)

# Answer to easy question 1: what share of passengers survived, by sex?
print("\nOverall survival rate:", round(titanic["Survived"].mean(), 3))
print("\nSurvival rate by sex:")
print(titanic.groupby("Sex")["Survived"].agg(["mean", "count"]).round(3))

# Answer to easy question 2: how did survival differ by ticket class?
print("\nSurvival rate by passenger class:")
print(titanic.groupby("Pclass")["Survived"].agg(["mean", "count"]).round(3))

# ---------------------------------------------------------------- Exercise 8
print("\n===== EXERCISE 8: messy import =====")
messy = (
    pd.read_csv(
        "messy.csv",
        sep=";",
        skiprows=2,
        na_values=["n/a", "-", "brak"],
        parse_dates=["order_date"],
        date_format="%d.%m.%Y",
    )
    .assign(price=lambda d: pd.to_numeric(
        d["price"].str.replace(r"[^\d.,-]", "", regex=True).str.replace(",", "."),
        errors="coerce"))
    .drop_duplicates(ignore_index=True)
)
print(messy)
print(messy.dtypes)
