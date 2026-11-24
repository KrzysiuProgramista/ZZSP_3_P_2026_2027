from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)

df = pd.read_csv("sales-selected-columns.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Revenue"] = df["Units Sold"] * df["Unit Price"]

# 1. Revenue per region (bar chart)
revenue_region = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(revenue_region.index, revenue_region.values / 1e6)
ax.set_title("Total revenue per region")
ax.set_xlabel("Region")
ax.set_ylabel("Revenue (million $)")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
fig.tight_layout()
fig.savefig(CHARTS_DIR / "ex1_1_revenue_per_region.png", dpi=150)
plt.close(fig)

# 2. Revenue per product (horizontal bar chart, sorted)
revenue_product = df.groupby("Item Type")["Revenue"].sum().sort_values()

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(revenue_product.index, revenue_product.values / 1e6)
ax.set_title("Total revenue per product")
ax.set_xlabel("Revenue (million $)")
ax.set_ylabel("Product (item type)")
fig.tight_layout()
fig.savefig(CHARTS_DIR / "ex1_2_revenue_per_product.png", dpi=150)
plt.close(fig)

# 3. Monthly revenue (line chart)
monthly = df.set_index("Order Date")["Revenue"].resample("MS").sum()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly.index, monthly.values / 1e6, marker=".")
ax.set_title("Monthly revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (million $)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(CHARTS_DIR / "ex1_3_monthly_revenue.png", dpi=150)
plt.close(fig)

# 4. Histogram of order values
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df["Revenue"] / 1e6, bins=20, edgecolor="white")
ax.set_title("Distribution of order values")
ax.set_xlabel("Order value (million $)")
ax.set_ylabel("Number of orders")
fig.tight_layout()
fig.savefig(CHARTS_DIR / "ex1_4_order_value_histogram.png", dpi=150)
plt.close(fig)

# 5. Box plot of order values per category
order = df.groupby("Item Type")["Revenue"].median().sort_values().index
data = [df.loc[df["Item Type"] == cat, "Revenue"] / 1e6 for cat in order]

fig, ax = plt.subplots(figsize=(12, 6))
ax.boxplot(data, tick_labels=order)
ax.set_title("Order values per category")
ax.set_xlabel("Category (item type)")
ax.set_ylabel("Order value (million $)")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
fig.tight_layout()
fig.savefig(CHARTS_DIR / "ex1_5_order_value_boxplot.png", dpi=150)
plt.close(fig)

print("Saved 5 charts.")
