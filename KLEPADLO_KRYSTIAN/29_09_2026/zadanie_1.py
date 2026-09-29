import pandas as pd

sales_df = pd.read_csv('sales.csv')
print(sales_df.head())
print(sales_df.shape)
print(sales_df.dtypes)
print(sales_df.columns.tolist())
sales_df.info(memory_usage="deep")