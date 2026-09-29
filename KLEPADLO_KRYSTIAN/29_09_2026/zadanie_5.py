import pandas as pd

sales_df = pd.read_csv('sales.csv')

sales_df.to_csv('sales_clean.csv', index=False)
sales_df.to_json('sales_clean.json', orient='records')
sales_df.to_excel('sales_clean.xlsx', index=False)

print(pd.read_csv('sales_clean.csv').shape == sales_df.shape)
print(pd.read_json('sales_clean.json', orient='records').shape == sales_df.shape)
print(pd.read_excel('sales_clean.xlsx').shape == sales_df.shape)