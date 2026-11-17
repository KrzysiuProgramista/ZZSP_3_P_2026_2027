import pandas as pd

# Load your sales dataset.
# Change "sales.csv" if your file has a different name.
df = pd.read_csv("sales.csv")

# 1. Total revenue per region
total_revenue_per_region = df.groupby("region")["total"].sum()
print("1. Total revenue per region:")
print(total_revenue_per_region)
print()

# 2. Average quantity per category
average_quantity_per_category = df.groupby("category")["quantity"].mean()
print("2. Average quantity per category:")
print(average_quantity_per_category)
print()

# 3. Number of orders per region
# size() counts all rows in each region.
orders_per_region = df.groupby("region").size()
print("3. Number of orders per region:")
print(orders_per_region)
print()

# 4. Revenue and average unit price per category
category_summary = df.groupby("category").agg(
    revenue=("total", "sum"),
    avg_unit_price=("unit_price", "mean")
)
print("4. Revenue and average unit price per category:")
print(category_summary)
print()

# 5. Range of order values per region (maximum - minimum)
order_value_range_per_region = df.groupby("region")["total"].agg(
    lambda values: values.max() - values.min()
)
print("5. Range of order values per region:")
print(order_value_range_per_region)
