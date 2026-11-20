# CityPulse — Smart City Traffic Intelligence

Rozwiązanie zespołowego zadania analitycznego **CityPulse Data Analytics Competition** (Rundy 1–5).

## Struktura folderu do oddania

```text
team_name/
├── data/                  # Oryginalne pliki CSV (niezmodyfikowane)
│   ├── traffic.csv
│   ├── sensors.csv
│   ├── weather.csv
│   └── incidents.csv
├── analysis.ipynb         # Powtarzalna analiza (Rundy 1–5) z tabelami i wykresami
├── dashboard.py           # Pipeline danych oraz funkcja city_dashboard(...)
├── team_briefing.pdf      # Raport końcowy dla miasta (Runda 5)
├── requirements.txt       # Zależności Pythona
└── README.md              # Niniejsza instrukcja
```

## Wymagania i instalacja

Wymagany Python 3.10+ oraz pakiety z pliku `requirements.txt` (`pandas`, `numpy`, `matplotlib`, `jupyter`):

```bash
pip install -r requirements.txt
```

## Jak uruchomić analizę

1. Upewnij się, że cztery niezmodyfikowane pliki CSV (`traffic.csv`, `sensors.csv`, `weather.csv`, `incidents.csv`) znajdują się w podkatalogu `data/`.
2. **Szybki test pipeline'u i dashboardu z terminala:**
   ```bash
   python dashboard.py
   ```
   Skrypt wykona integrację danych z raportem kontrolnym (`len()` przed i po każdym łączeniu, `validate=`, `indicator=`) oraz potwierdzi wygenerowanie wszystkich tabel funkcji `city_dashboard(traffic, sensors, weather, incidents)`.
3. **Pełna analiza i wykresy (Jupyter / VS Code):**
   Otwórz plik `analysis.ipynb` i wybierz **Run All**. Notatnik wygeneruje komplet wyników dla Rund 1–5, w tym wykres anomalii z 12 listopada 2026 w dzielnicy Riverside.

## Podsumowanie metodologii

- **Runda 1 (Integracja):** wszystkie łączenia wykonano jako `left join` względem `traffic.csv` (13 392 obserwacje), z kontrolą unikalności kluczy (`validate=`) i flagami dopasowania (`indicator=`). Wykazano 54 wiersze ruchu bez danych pogodowych (18 brakujących godzin-dzielnic) oraz 3 osierocone incydenty z nieznanymi `sensor_id` (`S-097`, `S-098`, `S-099`).
- **Runda 2 (Hotspoty):** zdefiniowano mapowanie dotkliwości (`low=1`, `moderate=2`, `high=3`, `critical=4`) oraz godziny szczytu (`07:00–09:00` i `16:00–18:00`).
- **Runda 3 (Szeregi czasowe):** zastosowano resampling dzienny (`resample("D")`), 3-dniową średnią kroczącą (`rolling(3)`), zmiany okresowe (`diff`, `pct_change`) oraz porównanie dni roboczych z weekendami.
- **Runda 4 (Anomalia 12.11.2026):** porównano godziny `07:00–12:59` w dzielnicy Riverside z bazą obejmującą te same godziny w 6 pobliskich dniach roboczych (`5, 6, 9, 10, 11, 13 listopada 2026`).