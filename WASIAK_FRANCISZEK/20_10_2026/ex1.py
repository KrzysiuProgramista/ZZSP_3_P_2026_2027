import pandas as pd

df = pd.read_csv("data.csv")

# 1. Keep rows where quantity is above 10.
print(df[df["quantity"] > 10])

# 2. Keep all sales in the North region.
print(df[df["region"] == "North"])

# 3. Keep Electronics sales in the North.
print(df[(df["category"] == "Electronics") & (df["region"] == "North")])

# 4. Keep unit prices from 400 to 1500, including both endpoints.
print(df[df["unit_price"].between(400, 1500)])

# 5. Exclude only Electronics sales in the South.
print(df[~((df["category"] == "Electronics") & (df["region"] == "South"))])

# 6. Keep North or East sales with quantity from 5 to 20, inclusive.
print(df[df["region"].isin(["North", "East"]) & df["quantity"].between(5, 20)])