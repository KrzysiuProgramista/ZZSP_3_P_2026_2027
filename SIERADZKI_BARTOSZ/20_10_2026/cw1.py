import pandas as pd
import io

csv_data = """Date,product,category,region,quantity,unit_price
2026-01-05,Laptop,Electronics,North,3,3500.00
2026-01-07,Mouse,Electronics,North,25,45.00
2026-01-12,Desk,Furniture,South,5,890.00
2026-01-15,Laptop,Electronics,South,2,3500.00
2026-01-19,Chair,Furniture,North,12,450.00
2026-02-02,Monitor,Electronics,East,8,1200.00
2026-02-08,Desk,Furniture,East,3,890.00
2026-02-14,Mouse,Electronics,West,40,45.00
2026-02-21,Laptop,Electronics,West,1,3500.00
2026-03-03,Chair,Furniture,South,20,450.00
2026-03-11,Monitor,Electronics,North,4,1200.00
2026-03-18,Keyboard,Electronics,East,15,199.00
2026-03-25,Desk,Furniture,West,7,890.00
2026-04-02,Laptop,Electronics,North,5,3500.00
2026-04-09,Chair,Furniture,East,9,450.00
2026-04-16,Keyboard,Electronics,South,30,199.00
2026-04-23,Monitor,Electronics,West,6,1200.00
2026-05-04,Desk,Furniture,North,2,890.00"""

df = pd.read_csv(io.StringIO(csv_data))

print("1. Quantity above 10:")
print(df[df['quantity'] > 10])

print("\n2. All sales in the North region:")
print(df[df['region'] == 'North'])

print("\n3. Electronics sold in the North:")
print(df[(df['category'] == 'Electronics') & (df['region'] == 'North')])

print("\n4. Unit price from 400 to 1,500 inclusive:")
print(df[df['unit_price'].between(400, 1500)])

print("\n5. Everything except Electronics in the South:")
print(df[~((df['category'] == 'Electronics') & (df['region'] == 'South'))])

print("\n6. Sales in North or East; quantity between 5 and 20:")
print(df[df['region'].isin(['North', 'East']) & df['quantity'].between(5, 20)])