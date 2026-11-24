"""Explore Librus grades locally. Never submit private PDFs or grades.csv."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

REQUIRED_COLUMNS = {"date", "subject", "grade", "description"}
SUMMARY_NOTE = (
    "Średnia bazowa nie jest oficjalną oceną semestralną: pomija wagi, "
    "plusy i minusy oraz zasady oceniania nauczyciela. "
    "Wpisy bez rozpoznanej oceny są liczone jako rekordy, "
    "ale nie wchodzą do średniej."
)


def load_grades(path: str | Path = "grades.csv") -> pd.DataFrame:
    """Load a local CSV; invalid dates and non-grade entries become missing."""
    df = pd.read_csv(path, dtype={"grade": "string", "subject": "string"})
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Brak wymaganych kolumn: {', '.join(sorted(missing))}")
    # The cleaned CSV uses unambiguous ISO dates: YYYY-MM-DD.
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    df["subject"] = df["subject"].str.strip()
    df["grade"] = df["grade"].str.strip()
    # Match a whole grade, so entries such as '16' or '50%' are not grades.
    extracted = df["grade"].str.extract(r"^[+-]?([1-6])[+-]?$", expand=False)
    df["grade_base"] = pd.to_numeric(extracted, errors="coerce")
    return df


def grades_below(df: pd.DataFrame, threshold: float = 3) -> pd.DataFrame:
    """Return records with base grades strictly below a finite threshold."""
    threshold = float(threshold)
    if not math.isfinite(threshold):
        raise ValueError("Próg musi być skończoną liczbą.")
    mask = df["grade_base"] < threshold
    return df.loc[mask.fillna(False)].copy()


def grades_for_subject(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """Search a literal subject fragment, ignoring case."""
    subject = subject.strip()
    if not subject:
        raise ValueError("Wpisz nazwę przedmiotu lub jej fragment.")
    mask = df["subject"].str.contains(subject, case=False, na=False, regex=False)
    return df.loc[mask].copy()


def parse_date(value: str) -> pd.Timestamp:
    """Parse an ISO calendar date for a query."""
    try:
        parsed = pd.to_datetime(value, format="%Y-%m-%d", errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError("Podaj poprawną datę w formacie YYYY-MM-DD.") from exc
    if pd.isna(parsed):
        raise ValueError("Data nie może być pusta.")
    return parsed


def grades_between_dates(
    df: pd.DataFrame, date_from: str, date_to: str
) -> pd.DataFrame:
    """Return records in an inclusive calendar-date range."""
    start, end = parse_date(date_from), parse_date(date_to)
    if start > end:
        raise ValueError("Data początkowa nie może być późniejsza od końcowej.")
    dates = df["date"].dt.normalize()
    mask = (dates >= start) & (dates <= end)
    return df.loc[mask].copy()


def report(df: pd.DataFrame, **filters: object) -> pd.DataFrame:
    """Combine exact column=value filters using AND; None selects missing."""
    unknown = set(filters) - set(df.columns)
    if unknown:
        raise ValueError(f"Nieznana kolumna: {', '.join(sorted(unknown))}")
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        condition = df[column].isna() if value is None else df[column].eq(value)
        mask &= condition.fillna(False)
    return df.loc[mask].copy()


def summary_by_subject(df: pd.DataFrame) -> pd.DataFrame:
    """Count all records and average recognized base grades by subject."""
    return (
        df.groupby("subject", dropna=False)
        .agg(record_count=("grade", "size"), average_base_grade=("grade_base", "mean"))
        .reset_index()
    )


def inspect_dataframe(df: pd.DataFrame) -> None:
    """Inspect the data locally without writing a report with private grades."""
    print("\nInformacje o danych (tylko w lokalnej konsoli):")
    df.info()
    print("\nPierwsze 5 rekordów:")
    print(df.head().to_string(index=False))
    print(f"\nBrakujące lub niepoprawne daty: {df['date'].isna().sum()}")
    print(f"Wpisy bez rozpoznanej oceny bazowej: {df['grade_base'].isna().sum()}")
    print(f"Brakujące/puste przedmioty: {df['subject'].fillna('').eq('').sum()}")


def read_filters(df: pd.DataFrame) -> dict[str, object]:
    """Read exact filters and convert console strings to the column type."""
    print("Kolumny:", ", ".join(df.columns))
    print("Filtry łączą się przez AND. Pusta nazwa kończy wpisywanie.")
    print("Tekst musi pasować dokładnie; <brak> oznacza brakującą wartość.")
    filters: dict[str, object] = {}
    while True:
        column = input("Kolumna: ").strip()
        if not column:
            return filters
        if column not in df.columns:
            raise ValueError(f"Nieznana kolumna: {column}")
        raw = input(f"Wartość dla {column}: ").strip()
        if raw == "<brak>":
            value = None
        elif is_datetime64_any_dtype(df[column]):
            value = parse_date(raw)
        elif is_numeric_dtype(df[column]):
            value = float(raw)
            if not math.isfinite(value):
                raise ValueError("Wartość musi być skończoną liczbą.")
        else:
            value = raw
        filters[column] = value


def show_result(result: pd.DataFrame) -> None:
    if result.empty:
        print("Brak pasujących rekordów.")
    else:
        print(result.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Lokalna analiza ocen z Librusa.")
    parser.add_argument(
        "csv_path", nargs="?", type=Path,
        default=Path(__file__).with_name("grades.csv"),
        help="Ścieżka do lokalnego CSV (domyślnie grades.csv obok programu).",
    )
    args = parser.parse_args()
    try:
        df = load_grades(args.csv_path.expanduser())
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"Nie można wczytać CSV: {exc}")
        print("Przygotuj lokalny CSV: date,subject,grade,description.")
        return
    if df.empty:
        print("Plik CSV nie zawiera rekordów.")
        return
    print("Dane pozostają na komputerze. Nie udostępniaj wyników z prywatnymi ocenami.")
    inspect_dataframe(df)
    while True:
        print(
            "\nLIBRUS — ANALIZA OCEN\n"
            "1. Oceny poniżej progu\n"
            "2. Wyszukiwanie przedmiotu\n"
            "3. Zakres dat\n"
            "4. Podsumowanie według przedmiotu\n"
            "5. Raport z wieloma filtrami\n"
            "6. Inspekcja danych\n"
            "0. Wyjście"
        )
        try:
            choice = input("Wybierz opcję: ").strip()
            if choice == "0":
                print("Do widzenia.")
                return
            if choice == "1":
                show_result(grades_below(df, input("Oceny poniżej: ")))
            elif choice == "2":
                show_result(grades_for_subject(df, input("Przedmiot lub fragment: ")))
            elif choice == "3":
                date_from = input("Od (YYYY-MM-DD): ").strip()
                date_to = input("Do (YYYY-MM-DD): ").strip()
                show_result(grades_between_dates(df, date_from, date_to))
            elif choice == "4":
                show_result(summary_by_subject(df))
                print(SUMMARY_NOTE)
            elif choice == "5":
                show_result(report(df, **read_filters(df)))
            elif choice == "6":
                inspect_dataframe(df)
            else:
                print("Nieznana opcja. Wybierz 0–6.")
        except (ValueError, TypeError) as exc:
            print(f"Niepoprawne dane: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nDo widzenia.")
            return


if __name__ == "__main__":
    main()
