# Instrukcje dla agenta AI/LLM — praca z biblioteką pandas

> Dokument bazuje na oficjalnym przewodniku "10 minutes to pandas"
> (https://pandas.pydata.org/docs/user_guide/10min.html) i ma służyć jako
> zestaw wytycznych dla agenta AI, który w przyszłości będzie generował lub
> analizował kod wykorzystujący pandas.

## 1. Konwencja importu

Agent zawsze powinien importować pandas i numpy w standardowy sposób:

```python
import numpy as np
import pandas as pd
```

## 2. Podstawowe struktury danych

- `Series` — jednowymiarowa, etykietowana tablica, może przechowywać dowolny
  typ danych (liczby, tekst, obiekty).
- `DataFrame` — dwuwymiarowa struktura tabelaryczna (wiersze + kolumny),
  odpowiednik arkusza kalkulacyjnego lub tabeli SQL.

Agent powinien domyślnie sięgać po `DataFrame`, gdy dane mają więcej niż
jedną kolumnę, a po `Series`, gdy operuje na pojedynczej kolumnie/wektorze.

## 3. Tworzenie obiektów

- Tworzenie `Series` z listy wartości: `pd.Series([...])`.
- Tworzenie `DataFrame` z tablicy numpy + indeksu dat: `pd.date_range()` do
  wygenerowania indeksu, następnie `pd.DataFrame(dane, index=..., columns=...)`.
- Tworzenie `DataFrame` ze słownika: klucze słownika stają się nazwami
  kolumn, wartości — danymi w kolumnach. Kolumny mogą mieć różne typy
  danych (`dtype`) — agent powinien to uwzględniać przy dalszym przetwarzaniu.

## 4. Podgląd i eksploracja danych

Zanim agent wykona jakąkolwiek transformację, powinien najpierw obejrzeć dane:

- `df.head(n)` / `df.tail(n)` — pierwsze/ostatnie n wierszy.
- `df.index`, `df.columns` — sprawdzenie etykiet wierszy i kolumn.
- `df.describe()` — szybkie statystyki opisowe (średnia, odchylenie, kwartyle).
- `df.to_numpy()` — konwersja do tablicy numpy (bez indeksu/nazw kolumn);
  agent powinien pamiętać, że przy mieszanych typach danych operacja ta
  może być kosztowna (kopiowanie danych do wspólnego typu `object`).
- `df.T` — transpozycja.
- `df.sort_index()` / `df.sort_values(by=...)` — sortowanie po indeksie lub
  wartościach.

## 5. Selekcja danych — rekomendowane metody

Agent generujący kod produkcyjny (nie tylko eksploracyjny) powinien
preferować jawne metody dostępu zamiast samego `[]`:

- `df.loc[]` — selekcja po etykietach (nazwach wierszy/kolumn).
- `df.iloc[]` — selekcja po pozycji liczbowej.
- `df.at[]` / `df.iat[]` — szybki dostęp do pojedynczej wartości
  (odpowiednio: po etykiecie / po pozycji).
- `df["kolumna"]` lub `df.kolumna` — wybór pojedynczej kolumny (atrybut
  działa tylko gdy nazwa kolumny jest poprawnym identyfikatorem Pythona).
- Filtrowanie warunkowe: `df[df["kolumna"] > wartość]`.
- `df["kolumna"].isin([...])` — filtrowanie po liście dopuszczalnych wartości.

## 6. Modyfikacja danych (setting)

- Dodanie nowej kolumny automatycznie dopasowuje dane po indeksie.
- Ustawianie wartości po etykiecie: `df.at[etykieta, "kolumna"] = wartość`.
- Ustawianie wartości po pozycji: `df.iat[i, j] = wartość`.
- Przypisanie całej kolumny z tablicy numpy: `df.loc[:, "kolumna"] = np.array([...])`.
- Operacje warunkowe (`df[df > 0] = ...`) pozwalają modyfikować dane
  spełniające zadany warunek.

## 7. Braki danych (missing data)

- Pandas reprezentuje braki jako `NaN` (domyślnie pomijane w obliczeniach).
- `df.reindex()` — zmiana/rozszerzenie indeksu lub kolumn (zwraca kopię).
- `df.dropna(how="any")` — usuwanie wierszy zawierających braki.
- `df.fillna(value=...)` — uzupełnianie braków zadaną wartością.
- `pd.isna(df)` — maska boolowska wskazująca braki danych.

Agent powinien zawsze jawnie decydować, czy braki danych mają być usunięte,
uzupełnione, czy pozostawione — nigdy nie ignorować tego problemu milcząco.

## 8. Operacje i statystyki

- Agregaty statystyczne: `df.mean()`, domyślnie liczone kolumnami
  (`axis=0`); `df.mean(axis=1)` liczy średnią wierszami.
- Operacje między obiektami o różnych indeksach automatycznie wyrównują
  dane (brakujące etykiety wypełniane są `NaN`).
- Funkcje użytkownika: `df.agg(funkcja)` redukuje dane, `df.transform(funkcja)`
  zwraca dane o tym samym kształcie co wejście.
- `Series.value_counts()` — zliczanie wystąpień unikalnych wartości.
- Metody tekstowe dostępne przez akcesor `.str`, np. `s.str.lower()`.

## 9. Łączenie danych

- `pd.concat([...])` — sklejanie obiektów wzdłuż wierszy (lub kolumn przy
  odpowiednim `axis`).
- `pd.merge(left, right, on="klucz")` — złączenie w stylu SQL (join) po
  wspólnej kolumnie/kluczu.
- Uwaga wydajnościowa: dodawanie kolumny jest tanie, dodawanie pojedynczych
  wierszy iteracyjnie jest kosztowne — agent powinien preferować budowę
  listy rekordów i jednorazowe utworzenie `DataFrame`, zamiast wielokrotnego
  dopisywania wierszy w pętli.

## 10. Grupowanie (split-apply-combine)

- `df.groupby("kolumna")` dzieli dane na grupy według wartości kolumny.
- Grupowanie po wielu kolumnach tworzy `MultiIndex` w wyniku.
- Do grup można stosować funkcje agregujące, np. `.sum()`.

## 11. Przekształcanie kształtu danych (reshaping)

- `df.stack()` — "kompresuje" poziom kolumn do indeksu (dane z szerokich
  stają się długie).
- `df.unstack()` — operacja odwrotna do `stack()`.
- `pd.pivot_table(df, values=..., index=..., columns=...)` — tworzenie
  tabeli przestawnej.

## 12. Szeregi czasowe

- `pd.date_range()` — generowanie indeksu dat.
- `Series.resample(reguła)` — zmiana częstotliwości próbkowania danych
  czasowych (np. agregacja sekundowych danych do 5-minutowych).
- `Series.tz_localize()` / `Series.tz_convert()` — obsługa stref czasowych.
- `pd.offsets.BusinessDay(n)` — dodawanie przesunięć czasowych
  uwzględniających dni robocze.

## 13. Dane kategoryczne

- Konwersja kolumny do typu kategorycznego: `df["kol"].astype("category")`.
- Zmiana nazw kategorii: `.cat.rename_categories([...])`.
- Ustawienie/uporządkowanie kategorii: `.cat.set_categories([...])`.
- Sortowanie danych kategorycznych odbywa się według kolejności kategorii,
  a nie leksykograficznie — agent powinien to uwzględniać przy sortowaniu.

## 14. Import/eksport danych

Agent powinien znać podstawowe formaty wejścia/wyjścia obsługiwane przez
pandas i dobierać je odpowiednio do kontekstu zadania:

| Format  | Zapis                  | Odczyt                  |
|---------|-------------------------|--------------------------|
| CSV     | `df.to_csv(sciezka)`    | `pd.read_csv(sciezka)`  |
| Parquet | `df.to_parquet(sciezka)`| `pd.read_parquet(sciezka)` |
| Excel   | `df.to_excel(sciezka, sheet_name=...)` | `pd.read_excel(sciezka, arkusz)` |

## 15. Typowe pułapki (gotchas), na które agent powinien uważać

- Nie wolno używać obiektu `Series`/`DataFrame` bezpośrednio w warunku
  logicznym `if`, `and`, `or` — zgłasza to `ValueError`, ponieważ wartość
  logiczna takiego obiektu jest niejednoznaczna. Zamiast tego należy użyć
  `.any()`, `.all()`, `.empty()` lub `.item()` w zależności od kontekstu.

## 16. Ogólne zalecenia dla agenta generującego kod z pandas

1. Zawsze sprawdzaj kształt i typy danych (`df.shape`, `df.dtypes`) przed
   transformacją.
2. Preferuj metody jawne (`loc`/`iloc`) nad niejednoznacznym `[]` w kodzie
   produkcyjnym.
3. Świadomie obsługuj brakujące dane — nie zostawiaj tego przypadkowi.
4. Unikaj iteracyjnego dopisywania wierszy do `DataFrame` — buduj dane
   zbiorczo.
5. Przy operacjach czasowych pamiętaj o strefach czasowych i częstotliwości
   próbkowania.
6. Dobieraj format zapisu/odczytu (CSV/Parquet/Excel) do wymagań
   wydajnościowych i kompatybilności zadania.
