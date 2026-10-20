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
    
    extracted = df["grade"].str.extract(r"([1-6])", expand=False)
    df["grade_base"] = pd.to_numeric(extracted, errors="coerce")
    return df


def grades_below(df: pd.DataFrame, threshold: float = 3) -> pd.DataFrame:
    """Return grade records whose base grade is below threshold."""
    return df[df["grade_base"] < threshold]


def grades_for_subject(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """Return grade records for a subject, ignoring letter case."""
    return df[df["subject"].str.contains(subject, case=False, na=False, regex=False)]


def grades_between_dates(df: pd.DataFrame, date_from: str, date_to: str) -> pd.DataFrame:
    """Return records dated in the inclusive range."""
    mask = (df["date"] >= pd.to_datetime(date_from)) & (df["date"] <= pd.to_datetime(date_to))
    return df[mask]


def report(df: pd.DataFrame, **filters: object) -> pd.DataFrame:
    """Apply any number of exact column=value filters."""
    for col in filters:
        if col not in df.columns:
            raise ValueError(f"Unknown column: {col}")
    
    result = df
    for col, value in filters.items():
        result = result[result[col] == value]
    return result


def summary_by_subject(df: pd.DataFrame) -> pd.DataFrame:
    """Return record count and mean base grade by subject."""
    return df.groupby("subject").agg(
        record_count=("grade", "count"),
        average_base_grade=("grade_base", "mean")
    ).reset_index()


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
