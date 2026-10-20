# Pandas – ćwiczenia 1–8 (29.09.2026)

Katalog: `SURNAME_NAME/29.09.2026/` (zmień `SURNAME_NAME` na swoje NAZWISKO_IMIĘ).

## Zawartość katalogu

| Plik | Opis |
|------|------|
| `README.md` | Ten plik – instrukcje |
| `sales.csv`, `sales_pl.csv`, `products.json`, `messy.csv` | Dane do ćwiczeń |
| `inspect_utils.py` | Funkcja `inspect(df, name)` z ćwiczenia 3 (do reużycia) |
| `ex01_05.py` | Rozwiązania ćwiczeń 1–5 |
| `ex07_titanic.py`, `ex07_titanic_notes.md` | Ćwiczenie 7 (skrypt + pytania) |
| `ex08_messy.py` | Ćwiczenie 8 |

Uruchomienie: `python ex01_05.py`, `python ex08_messy.py`, `python ex07_titanic.py Titanic-Dataset.csv` (potrzebne: `pandas`, `openpyxl`).
Pliki wynikowe (`sales_clean.csv`, `.json`, `.xlsx`) pojawią się w tym samym katalogu.

---

## Exercise 1: Basic CSV reading
Wczytaj `sales.csv` do `sales_df`. Wypisz pierwsze 5 wierszy, shape, dtypes,
nazwy kolumn oraz zużycie pamięci (`df.info(memory_usage="deep")`).

## Exercise 2: The awkward file
Wczytaj `sales_pl.csv` (separator `;`, przecinek dziesiętny, polskie nazwy kolumn).
Kolumny liczbowe mają być numeryczne. Zmień nazwy na angielskie przez
`df.rename(columns={...})` i sprawdź `.dtypes` (nic liczbowego nie może zostać `object`).

## Exercise 3: A first-pass inspection routine
Napisz `inspect(df)`, która wypisuje:
- shape,
- nazwy kolumn z dtypes,
- liczbę i % braków na kolumnę,
- liczbę zduplikowanych wierszy,
- dla kolumn numerycznych: min, max, mean, median,
- dla kolumn `object`: liczbę unikalnych wartości i 3 najczęstsze.

Przetestuj na obu plikach. (W `inspect_utils.py` jest też alias `inspect_df`.)

## Exercise 4: Reading JSON
Wczytaj `products.json`. Zagnieżdżone obiekty stają się słownikami w komórkach.
Spłaszcz przez `pd.json_normalize` i porównaj oba wyniki.

## Exercise 5: Writing files
Zapisz oczyszczone dane sprzedaży do `sales_clean.csv` (bez indeksu), do JSON
(`orient="records"`) i do Excela (`pip install openpyxl`). Wczytaj każdy z powrotem
i potwierdź, że dane są takie same.

## Exercise 7: An unfamiliar dataset
Pobierz Titanica: https://www.kaggle.com/datasets/yasserh/titanic-dataset
(zapisz jako `Titanic-Dataset.csv` w tym katalogu). Uruchom `inspect()`, zapisz 5 pytań,
odpowiedz na 2 najłatwiejsze, zapisz 2 pytania, na które NIE da się odpowiedzieć,
i jakich danych brakuje. Szczegóły w `ex07_titanic_notes.md`.

## Exercise 8: The messy import
`messy.csv` ma: 2 śmieciowe linie przed nagłówkiem, braki jako `n/a`, `-`, `brak`
i puste, cenę z walutą, datę w formacie DD.MM.YYYY oraz duplikaty.
Wczytaj do czystego DataFrame (poprawne dtypes, bez duplikatów), jak najmniejszą
liczbą linii, i opisz każdy użyty parametr wraz z uzasadnieniem.