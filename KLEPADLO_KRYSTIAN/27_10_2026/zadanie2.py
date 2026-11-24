import pandas as pd
import numpy as np

def quality_report(df):
    """Funkcja raportu jakości danych (zgodna ze slajdem)."""
    print("=" * 60)
    print(" RAPORT JAKOŚCI DANYCH (DATA QUALITY REPORT)")
    print("=" * 60)
    print(f"Całkowita liczba wierszy: {len(df)}")
    print(f"Całkowita liczba kolumn: {len(df.columns)}")
    
    duplicate_rows = int(df.duplicated().sum())
    print(f"Liczba zduplikowanych wierszy: {duplicate_rows}")
    print("-" * 60)
    
    report_data = []
    n_rows = len(df)
    
    for col in df.columns:
        s = df[col]
        dtype = s.dtype
        missing_count = int(s.isna().sum())
        missing_pct = round((missing_count / n_rows) * 100, 2) if n_rows > 0 else 0.0
        unique_count = int(s.nunique())
        
        if pd.api.types.is_numeric_dtype(dtype):
            c_min = s.min()
            c_max = s.max()
            c_mean = s.mean()
            std_val = s.std()
            
            if std_val > 0 and not pd.isna(std_val):
                outliers = int(((s - s.mean()).abs() > 3 * std_val).sum())
            else:
                outliers = 0
        else:
            c_min = c_max = c_mean = outliers = np.nan
            
        is_constant = unique_count == 1
        is_identifier = (unique_count == n_rows) and (n_rows > 0)
        category_hint = (dtype == 'object' or pd.api.types.is_string_dtype(dtype)) and (unique_count < 20) and not is_constant
        
        report_data.append({
            "column": col,
            "dtype": dtype,
            "missing_count": missing_count,
            "missing_%": missing_pct,
            "unique_count": unique_count,
            "min": c_min,
            "max": c_max,
            "mean": c_mean,
            "outliers_3std": outliers,
            "constant_col": is_constant,
            "identifier": is_identifier,
            "category_hint": category_hint
        })
        
    report_df = pd.DataFrame(report_data).set_index("column")
    return report_df
# --- 1. WCZYTANIE DANYCH ---
# Wczytujemy plik CSV, który dostałeś
df = pd.read_csv("dirty_data.csv")

print("--- ORYGINALNE DANE (SUROWE) ---")
print(df.head(10))
print("\n" + "="*60 + "\n")

# --- 2. CZYSZCZENIE DANYCH (DATA CLEANING) ---

# A. Czyszczenie cen i ilości (usuwanie spacji w tysiącach np. '3 500.00' -> '3500.00' i zmiana na float/int)
if df['price'].dtype == object:
    df['price'] = df['price'].astype(str).str.replace(' ', '').astype(float)

if df['quantity'].dtype == object:
    df['quantity'] = df['quantity'].astype(str).str.replace(' ', '')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')

# B. Usuwanie dokładnych duplikatów wierszy (w danych masz zduplikowany wiersz nr 10)
df = df.drop_duplicates()

# C. Czyszczenie tekstów (usunięcie zbędnych spacji wokół nazw produktów i regionów)
df['product'] = df['product'].astype(str).str.strip().replace('nan', np.nan)
df['category'] = df['category'].astype(str).str.strip().replace('nan', np.nan)
df['region'] = df['region'].astype(str).str.strip().str.title().replace('Nan', np.nan) # Ujednolicenie wielkości liter (np. north -> North)

# D. Poprawa błędów logicznych (np. ujemna ilość -40 zmieniona na NaN lub usunięta; kosmiczna cena 99999.00)
df.loc[df['quantity'] < 0, 'quantity'] = np.nan
df.loc[df['price'] > 50000, 'price'] = np.nan # odrzucenie oczywistej bzdury cenowej

# --- 3. URUCHOMIENIE RAPORTU JAKOŚCI ---
report = quality_report(df)
print(report)