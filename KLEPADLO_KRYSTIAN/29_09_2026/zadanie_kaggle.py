import pandas as pd
import sys
import os

# Wymuszenie kodowania UTF-8 w terminalu
sys.stdout.reconfigure(encoding='utf-8')

def inspect(df):
    print(f"Shape: {df.shape}")
    print(df.dtypes)
    missing = df.isnull().sum()
    print(pd.DataFrame({'Count': missing, 'Pct (%)': (missing / len(df)) * 100}))
    print(f"Duplicates: {df.duplicated().sum()}")
    num_cols = df.select_dtypes(include='number').columns
    if not num_cols.empty:
        print(df[num_cols].agg(['min', 'max', 'mean', 'median']))
    for col in df.select_dtypes(include=['object', 'str']).columns:
        print(f"\n{col}:\nUnique: {df[col].nunique()}\nTop 3:\n{df[col].value_counts().head(3)}")

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'diamonds.csv')

# 1. Wczytanie danych
try:
    df_diamonds = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"BŁĄD: Brak pliku {file_path}. Pobierz go z Kaggle i umieść w folderze ze skryptem.")
    sys.exit(1)

# 2. Inspekcja
print("--- INSPEKCJA DANYCH ---")
inspect(df_diamonds)

# 3. Prezentacja wyników i możliwości analitycznych
print("\n--- PREZENTACJA: MOŻLIWOŚCI ANALIZY ZBIORU DIAMONDS ---")
print("1. Wycena wartości rynkowej (Price Prediction):")
print("   - Zbudowanie modelu przewidującego cenę na podstawie masy (carat) oraz wymiarów fizycznych (x, y, z).")
print("\n2. Wpływ jakości na opłacalność:")
print("   - Badanie korelacji między szlifem (cut), barwą (color) i czystością (clarity) a końcową ceną w dolarach.")
print("\n3. Weryfikacja proporcji i anomalii:")
print("   - Identyfikacja kamieni o nietypowych parametrach geometrycznych (np. błędy w szerokości tafli - 'table' lub głębokości - 'depth'), które mogą wskazywać na błędną wycenę.")
print("\n4. Optymalizacja zakupowa:")
print("   - Segmentacja diamentów w celu określenia przedziałów wagowych oferujących najlepszy stosunek wielkości do ceny, kluczowy przy projektowaniu spersonalizowanej biżuterii.")