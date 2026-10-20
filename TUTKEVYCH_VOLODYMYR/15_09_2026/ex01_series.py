import numpy as np
import pandas as pd

# Series z listy 6 liczb - indeks domyślny to 0..5 (RangeIndex)
s = pd.Series([10, 20, 15, 30, 25, 5])
print(s)
print("Index:", s.index)

# Series z własnym indeksem tekstowym
s = pd.Series([10, 20, 15, 30, 25, 5], index=["a", "b", "c", "d", "e", "f"], name="wartosci")
print(s)

# Series ze słownika - KLUCZE słownika stają się indeksem
s_dict = pd.Series({"x": 1, "y": 2, "z": 3})
print(s_dict)

# Dostęp po etykiecie i po pozycji
print(s["a"])       # po etykiecie
print(s.iloc[0])    # po pozycji

# Atrybuty
print(s.values)
print(s.index)
print(s.dtype)
print(s.name)

# Arytmetyka na całej Series (wektorowo, bez pętli)
print(s * 2)
print(s + 10)
print(s > 15)       # Series typu bool
