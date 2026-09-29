import pandas as pd
import os

# Zbuduj pełną ścieżkę do pliku messy.csv w tym samym folderze co ten skrypt
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'messy.csv')

df = pd.read_csv(
    file_path,
    sep=';',
    skiprows=2,
    na_values=["n/a", "-", "brak"],
    parse_dates=['order_date'],
    dayfirst=True
).drop_duplicates()

df['price'] = df['price'].str.replace(' PLN', '', regex=False).str.replace(' ', '', regex=False).str.replace(',', '.', regex=False).astype(float)

print(df.dtypes)
print(df)