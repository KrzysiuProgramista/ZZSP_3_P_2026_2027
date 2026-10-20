import pandas as pd
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'sales.csv')

# Pomiar dla pełnego pliku
start_full = time.perf_counter()
df_full = pd.read_csv(file_path)
time_full = time.perf_counter() - start_full

# Pomiar z ograniczeniami (kolumny i wiersze)
start_opt = time.perf_counter()
df_opt = pd.read_csv(file_path, usecols=['date', 'product', 'quantity'], nrows=10)
time_opt = time.perf_counter() - start_opt

print(df_opt)
print(f"\nCzas pełnego wczytywania: {time_full:.6f} s")
print(f"Czas optymalnego wczytywania: {time_opt:.6f} s")