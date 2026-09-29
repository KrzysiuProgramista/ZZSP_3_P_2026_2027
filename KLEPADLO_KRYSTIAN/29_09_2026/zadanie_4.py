import pandas as pd
import json

products_df = pd.read_json('products.json')
with open('products.json', 'r') as f:
    products_flat = pd.json_normalize(json.load(f))
    
print(products_df)
print(products_flat)