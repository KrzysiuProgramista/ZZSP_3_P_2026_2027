import pandas as pd

df = pd.read_csv("data.csv")
df["total"] = df["quantity"] * df["unit_price"]

print(df.groupby("region")["total"].sum())

print(df.groupby("category")["quantity"].mean())

print(df.groupby("region").size())

print(df.groupby("category").agg(
    revenue=("total", "sum"),
    avg_unit_price=("unit_price", "mean")
))


def value_range(series):
    return series.max() - series.min()


print(df.groupby("region")["total"].agg(value_range))
