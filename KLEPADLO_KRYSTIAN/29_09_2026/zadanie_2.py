import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'sales_pl.csv')

sales_pl_df = pd.read_csv(file_path, sep=';', decimal=',')
sales_pl_df = sales_pl_df.rename(columns={
    'data': 'date', 'produkt': 'product', 'kategoria': 'category',
    'region': 'region', 'ilosc': 'quantity', 'cena_jednostkowa': 'unit_price'
})
print(sales_pl_df.dtypes)