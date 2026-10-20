# 1
df[df["quantity"] > 10]

# 2
df[df["region"] == "North"]

# 3
df[(df["category"] == "Electronics") & (df["region"] == "North")]

# 4
df[df["unit_price"].between(400, 1500)]

# 5
df[~((df["category"] == "Electronics") & (df["region"] == "South"))]

# 6
df[df["region"].isin(["North", "East"]) & df["quantity"].between(5, 20)]