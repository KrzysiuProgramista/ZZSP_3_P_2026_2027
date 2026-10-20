"""Librus Intelligence — student starter code.

Before running, create grades.csv from your own Librus PDF locally.
Keep the PDF and grades.csv private; do not submit them or commit them to Git.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"date", "subject", "grade", "description"}


def load_grades(path: str | Path = "grades.csv") -> pd.DataFrame:
    """Load the cleaned CSV and add parsed date and base-grade columns."""
    df = pd.read_csv(path, dtype={"grade": "string", "subject": "string"})
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["subject"] = df["subject"].astype("string").str.strip()
    df["grade"] = df["grade"].astype("string").str.strip()
    # Example: '4+' and '4-' both have base grade 4. This is not an official grade average.
    extracted = df["grade"].str.extract(r"([1-6])", expand=False)
    df["grade_base"] = pd.to_numeric(extracted, errors="coerce")
    return df


def grades_below(df: pd.DataFrame, threshold: float = 3) -> pd.DataFrame:
    """Return grade records whose base grade is below threshold. TODO: implement."""
    # TODO: use a boolean mask and return matching rows.
    raise NotImplementedError


def grades_for_subject(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """Return grade records for a subject, ignoring letter case. TODO: implement."""
    # TODO: use .str.contains(..., case=False, na=False, regex=False).
    raise NotImplementedError


def grades_between_dates(df: pd.DataFrame, date_from: str, date_to: str) -> pd.DataFrame:
    """Return records dated in the inclusive range. TODO: implement."""
    # TODO: convert both limits to datetime and use a boolean mask.
    raise NotImplementedError


def report(df: pd.DataFrame, **filters: object) -> pd.DataFrame:
    """Apply any number of exact column=value filters. TODO: implement."""
    # TODO: validate every column, combine filters, and raise ValueError for an unknown column.
    raise NotImplementedError


def summary_by_subject(df: pd.DataFrame) -> pd.DataFrame:
    """Return record count and mean base grade by subject. TODO: implement."""
    # TODO: use groupby() and agg() or build the summary another readable way.
    raise NotImplementedError


def main() -> None:
    try:
        df = load_grades()
    except FileNotFoundError:
        print("grades.csv was not found. Create it from your own Librus PDF first.")
        return
    except (ValueError, pd.errors.EmptyDataError) as exc:
        print(f"Could not load grades.csv: {exc}")
        return

    if df.empty:
        print("grades.csv contains no grade records yet. Add records and try again.")
        return

    while True:
        print("\nLIBRUS INTELLIGENCE")
        print("1. Show grades below a base grade")
        print("2. Search by subject")
        print("3. Search by date range")
        print("4. Summary by subject")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                threshold = float(input("Show base grades below: "))
                print(grades_below(df, threshold).to_string(index=False))
            elif choice == "2":
                subject = input("Subject name (or part of it): ").strip()
                print(grades_for_subject(df, subject).to_string(index=False))
            elif choice == "3":
                date_from = input("Date from (YYYY-MM-DD): ").strip()
                date_to = input("Date to (YYYY-MM-DD): ").strip()
                print(grades_between_dates(df, date_from, date_to).to_string(index=False))
            elif choice == "4":
                print(summary_by_subject(df).to_string(index=False))
            elif choice == "5":
                print("Goodbye.")
                break
            else:
                print("Unknown option. Choose 1–5.")
        except (ValueError, NotImplementedError) as exc:
            print(f"This option is not ready or the input is invalid: {exc}")


if __name__ == "__main__":
    main()
