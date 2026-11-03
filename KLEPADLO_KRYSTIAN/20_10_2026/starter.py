"""Librus Intelligence — student starter code."""
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
    start = pd.to_datetime(date_from)
    end = pd.to_datetime(date_to)
    return df[(df["date"] >= start) & (df["date"] <= end)]
def report(df: pd.DataFrame, **filters: object) -> pd.DataFrame:
    """Apply any number of exact column=value filters."""
    filtered_df = df.copy()
    for col, val in filters.items():
        if col not in filtered_df.columns:
            raise ValueError(f"Unknown column: {col}. Available columns: {', '.join(filtered_df.columns)}")
        filtered_df = filtered_df[filtered_df[col] == val]
    return filtered_df

def summary_by_subject(df: pd.DataFrame) -> pd.DataFrame:
    """Return record count and mean base grade by subject."""
    summary = df.groupby("subject").agg(
        record_count=("grade", "count"),
        mean_base_grade=("grade_base", "mean")
    ).reset_index()
    return summary

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
                print("\nNote: 'mean_base_grade' is a standard arithmetic mean of the extracted integers. It does not account for Librus category weights (e.g., tests vs. homework) or modifier signs (+/-). Therefore, it is not the official term grade.")
            elif choice == "5":
                print("Goodbye.")
                break
            else:
                print("Unknown option. Choose 1–5.")
        except (ValueError, NotImplementedError) as exc:
            print(f"This option is not ready or the input is invalid: {exc}")

if __name__ == "__main__":
    main()