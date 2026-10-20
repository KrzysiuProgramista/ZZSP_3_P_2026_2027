import numpy as np
import pandas as pd

a = pd.Series([1, 2, 3], index=["a", "b", "c"])
b = pd.Series([10, 20, 30], index=["b", "c", "d"])

# Dodawanie łączy wartości po ETYKIETACH indeksu, nie po pozycji.
# Wynik ma sumę indeksów (a, b, c, d). "a" jest tylko w a, "d" tylko w b -
# brak pary, więc wynik to NaN (a + brak = NaN). b i c mają parę: 2+10, 3+20.
print(a + b)

# .add(fill_value=0) traktuje brakującą wartość jako 0, więc NaN znikają:
# a = 1+0, d = 0+30. (Tylko gdy etykieta brakuje w jednej Series;
# gdyby brakowało w obu, zostałby NaN.)
print(a.add(b, fill_value=0))

# Dlaczego indeks odróżnia pandas od listy list:
# w liście list wartość identyfikuje tylko jej pozycja, więc operacje
# na dwóch listach łączą element nr i z elementem nr i - nawet jeśli
# dotyczą różnych rzeczy. W pandas każda wartość ma etykietę (uczeń, dzień,
# data), a operacje, łączenia i wybieranie dopasowują dane po etykietach.
# Dane pozostają poprawne po sortowaniu, filtrowaniu czy przestawieniu wierszy.
