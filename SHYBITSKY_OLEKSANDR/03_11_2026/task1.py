import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")

print("Ex 1")
print(df.assign(revenue=df["quantity"] * df["unit_price"]).groupby("region")["revenue"].sum())
print("Ex 2")
print(df.groupby("category")["quantity"].mean())
print("Ex 3")
print(df.groupby("region").size())
print("Ex 4")
print(df.assign(revenue=df["quantity"] * df["unit_price"]).groupby("category").agg(total_revenue=("revenue", "sum"), avg_price=("unit_price", "mean")))
print("Ex 5")
df.assign(order_value=df["quantity"] * df["unit_price"]).groupby("region")["order_value"].agg(lambda x: x.max() - x.min())
