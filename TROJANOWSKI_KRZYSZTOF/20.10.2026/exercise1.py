import pandas as pa

df = pa.read_csv("data.csv")

#1
print(df.query("quantity > 10"))

#2
print(df.query("region == 'North'"))

#3
print(df.query("region == 'North' and category == 'Electronics'"))

#4
print(df[df["unit_price"].between(400, 1500)])

#5
print(df.query("not (region == 'South' and category == 'Electronics')"))

#6
print(df.query("region == 'North' or region == 'East'")[df["unit_price"].between(5, 20)])
