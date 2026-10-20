import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
products_df = pd.read_json(BASE_DIR / "products.json")

print("=== Read with pd.read_json ===")
print(products_df)
print("\nNested supplier cell:")
print(products_df.loc[0, "supplier"])
print("Type:", type(products_df.loc[0, "supplier"]))

flattened_df = pd.json_normalize(products_df.to_dict(orient="records"))

print("\n=== Flattened with pd.json_normalize ===")
print(flattened_df)
print("\nOriginal columns:", products_df.columns.tolist())
print("Flattened columns:", flattened_df.columns.tolist())
print("Original shape:", products_df.shape)
print("Flattened shape:", flattened_df.shape)
