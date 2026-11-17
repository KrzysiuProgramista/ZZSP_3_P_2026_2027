import pandas as pd

df = pd.DataFrame({
    "order_id": range(1, 13),
    "region": ["North", "South", "East", "West"] * 3,
    "category": ["Tools", "Toys", "Tools", "Food", "Food", "Toys",
                 "Tools", "Food", "Toys", "Tools", "Food", "Toys"],
    "quantity": [3, 1, 5, 2, 4, 6, 2, 3, 1, 7, 2, 4],
    "unit_price": [10.0, 25.5, 9.0, 4.5, 5.0, 22.0,
                   11.5, 4.0, 30.0, 8.5, 6.0, 19.0],
})
df["revenue"] = df["quantity"] * df["unit_price"]

#1
print("1. Total revenue per region")
print(df.groupby("region")["revenue"].sum(), "\n")

#2
print("2. Average quantity per category")
print(df.groupby("category")["quantity"].mean(), "\n")

#3
print("3. Number of orders per region")
print(df.groupby("region").size(), "\n")

#4
print("4. Revenue and average unit price per category")
print(df.groupby("category").agg(
    revenue=("revenue", "sum"),
    avg_unit_price=("unit_price", "mean"),
), "\n")

#5
print("5. Range of order values per region")
print(df.groupby("region")["revenue"].agg(lambda s: s.max() - s.min()))