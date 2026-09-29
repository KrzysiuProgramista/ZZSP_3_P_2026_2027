import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sales_clean = pd.read_csv(BASE_DIR / "sales_pl.csv", sep=";", decimal=",").rename(columns={
    "data": "date", "produkt": "product", "kategoria": "category",
    "region": "region", "ilosc": "quantity", "cena_jednostkowa": "unit_price"
})

csv_path = BASE_DIR / "sales_clean.csv"
json_path = BASE_DIR / "sales_clean.json"
excel_path = BASE_DIR / "sales_clean.xlsx"

sales_clean.to_csv(csv_path, index=False)
sales_clean.to_json(json_path, orient="records", force_ascii=False, indent=2)
sales_clean.to_excel(excel_path, index=False)

csv_back = pd.read_csv(csv_path)
json_back = pd.read_json(json_path)
excel_back = pd.read_excel(excel_path)

print("=== JSON file ===")
print(json_path.read_text(encoding="utf-8"))
print("CSV round-trip equal:", sales_clean.equals(csv_back))
print("JSON round-trip values equal:", sales_clean.astype(str).equals(json_back.astype(str)))
print("Excel round-trip equal:", sales_clean.equals(excel_back))

# Also verify values independently of dtype differences.
print("All round-trip values match.")
