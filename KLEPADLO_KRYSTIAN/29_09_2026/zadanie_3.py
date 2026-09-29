import pandas as pd

def inspect(df):
    print(f"Shape: {df.shape}")
    print(df.dtypes)
    missing = df.isnull().sum()
    print(pd.DataFrame({'Count': missing, 'Pct (%)': (missing / len(df)) * 100}))
    print(f"Duplicates: {df.duplicated().sum()}")
    num_cols = df.select_dtypes(include='number').columns
    if not num_cols.empty:
        print(df[num_cols].agg(['min', 'max', 'mean', 'median']))
    for col in df.select_dtypes(include='object').columns:
        print(f"\n{col}:\nUnique: {df[col].nunique()}\nTop 3:\n{df[col].value_counts().head(3)}")

sales_df = pd.read_csv('sales.csv')
sales_pl_df = pd.read_csv('sales_pl.csv', sep=';', decimal=',')
sales_pl_df = sales_pl_df.rename(columns={
    'data': 'date', 'produkt': 'product', 'kategoria': 'category',
    'region': 'region', 'ilosc': 'quantity', 'cena_jednostkowa': 'unit_price'
})

inspect(sales_df)
inspect(sales_pl_df)