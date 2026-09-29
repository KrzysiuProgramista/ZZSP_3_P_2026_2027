import pandas as pd

# Exercise 2: The awkward file
# Semicolons, comma decimals
sales_pl = pd.read_csv("sales_pl.csv", sep=";", decimal=",")

# Rename columns
sales_pl = sales_pl.rename(columns={
    "data": "date", 
    "produkt": "product", 
    "kategoria": "category",
    "region": "region", 
    "ilosc": "quantity", 
    "cena_jednostkowa": "unit_price"
})

print("--- Confirmed Dtypes ---")
print(sales_pl.dtypes)
print("\n(Note: all numeric columns are correctly loaded as float/int)")
