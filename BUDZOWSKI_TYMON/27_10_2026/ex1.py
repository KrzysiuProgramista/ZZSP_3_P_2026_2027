import pandas as pd

df = pd.read_csv("data.csv")

print(df.head())
print(df.dtypes)   
print(df.shape)     

df["total"] = df["quantity"] * df["unit_price"]
df["total_with_vat"] = (df["total"] * 1.23).round(2)
df["unit_price_eur"] = (df["unit_price"] / 4.3).round(2)

print(df[["product", "quantity", "unit_price", "total",
          "total_with_vat", "unit_price_eur"]])
print(df[["total", "total_with_vat", "unit_price_eur"]].dtypes)