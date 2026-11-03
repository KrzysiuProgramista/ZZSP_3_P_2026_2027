import pandas as pd

# Load data and create the total column
df = pd.read_csv("data.csv")
df["total"] = df["quantity"] * df["unit_price"]

# 1. Total revenue per region
revenue_by_region = df.groupby("region")["total"].sum()
print("1. Total revenue per region")
print(revenue_by_region, "\n")

# 2. Average quantity per category
avg_qty_by_category = df.groupby("category")["quantity"].mean()
print("2. Average quantity per category")
print(avg_qty_by_category, "\n")

# 3. Number of orders per region (size counts rows, including NaN)
orders_by_region = df.groupby("region").size()
print("3. Orders per region")
print(orders_by_region, "\n")

# 4. Revenue and average unit price per category
category_summary = df.groupby("category").agg(
    revenue=("total", "sum"),
    avg_unit_price=("unit_price", "mean")
)
print("4. Revenue and average unit price per category")
print(category_summary, "\n")

# 5. Range of order values per region (max - min)
def value_range(series):
    return series.max() - series.min()

range_by_region = df.groupby("region").agg(
    order_range=("total", value_range)
)
print("5. Order value range per region")
print(range_by_region)