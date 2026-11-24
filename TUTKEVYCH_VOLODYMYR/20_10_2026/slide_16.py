from pathlib import Path
import pandas as pd

df = pd.read_csv(Path(__file__).parent / "data.csv")

# 01. Quantity above 10
print(df[df["quantity"] > 10])

# 02. All sales in the North region
print(df[df["region"] == "North"])

# 03. Electronics sold in the North
print(df[(df["category"] == "Electronics") & (df["region"] == "North")])

# 04. Unit price from 400 to 1,500 inclusive
print(df[df["unit_price"].between(400, 1500)])

# 05. Everything except Electronics in the South
print(df[~((df["category"] == "Electronics") & (df["region"] == "South"))])

# 06. Sales in North or East; quantity between 5 and 20
print(df[df["region"].isin(["North", "East"]) & df["quantity"].between(5, 20)])
