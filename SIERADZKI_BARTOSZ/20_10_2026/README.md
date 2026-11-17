# Uruchomienie

W terminalu otwartym w tym folderze:

```bash
python3 -m pip install -r requirements.txt
```

Demonstracja na fikcyjnych danych:

```bash
python3 starter.py fictional_grades.csv
```

Testy:

```bash
python3 -m pytest test_starter.py -v
```

## Prywatne dane — wykonaj samodzielnie na swoim komputerze

1. Wyeksportuj PDF z Librusa.
2. Uruchom lokalnie:

   ```bash
   python3 inspect_librus_pdf.py "/pełna/ścieżka/do/eksportu.pdf"
   ```

3. Sprawdź tabele w `private_work` i przygotuj `grades.csv` z nagłówkiem:

   ```text
   date,subject,grade,description
   ```

   Daty zapisuj jako `YYYY-MM-DD`. Jeden wiersz to jeden wpis.
   Tekst zawierający przecinek ujmij w cudzysłów.
   Inspektor nie tworzy automatycznie oczyszczonego `grades.csv`.
4. Umieść `grades.csv` obok `starter.py` i uruchom:

   ```bash
   python3 starter.py
   ```

   Możesz też podać pełną ścieżkę do CSV jako argument.

Menu: 1 — poniżej progu, 2 — przedmiot, 3 — zakres dat,
4 — podsumowanie, 5 — wiele filtrów, 6 — inspekcja, 0 — wyjście.
W opcji 5 podawaj kolejno nazwę kolumny i wartość. Pusta nazwa kolumny
uruchamia raport. Filtry tekstowe są dokładne i rozróżniają wielkość liter.
Wpisz `<brak>`, aby wyszukać brakującą wartość.

Do oddania: kod, zależności i `RAPORT.md`. Dane fikcyjne są opcjonalne.
Nie oddawaj prywatnego PDF, CSV ani folderu `private_work`.
