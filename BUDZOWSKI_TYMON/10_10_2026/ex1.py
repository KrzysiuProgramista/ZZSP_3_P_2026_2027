import pandas as pd

df = pd.read_csv("data.csv")

print(df[df["quantity"] > 10])

print(df[df["region"] == "North"])

print(df[(df["category"] == "Electronics") & (df["region"] == "North")])

print(df[df["unit_price"].between(400, 1500)])

print(df[~((df["category"] == "Electronics") & (df["region"] == "South"))])

print(df[df["region"].isin(["North", "East"]) & df["quantity"].between(5, 20)])