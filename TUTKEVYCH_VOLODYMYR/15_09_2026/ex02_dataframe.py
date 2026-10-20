import numpy as np
import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(data)
print(df_grades)

print(df_grades.shape)     # (wiersze, kolumny) = (5, 4)
print(df_grades.columns)
print(df_grades.index)     # RangeIndex 0..4
# Uwaga (pandas 3.0): "student" ma dtype str, nie object; oceny to int64
print(df_grades.dtypes)

# info(): liczba wierszy, zakres indeksu, dla każdej kolumny nazwa, liczba
# niepustych wartości (Non-Null Count) i dtype, na końcu zużycie pamięci
df_grades.info()

# describe() - statystyki kolumn liczbowych:
#   count - liczba niepustych wartości
#   mean  - średnia
#   std   - odchylenie standardowe
#   min   - wartość minimalna
#   25%   - pierwszy kwartyl (25% wartości jest mniejsze)
#   50%   - mediana
#   75%   - trzeci kwartyl
#   max   - wartość maksymalna
print(df_grades.describe())
