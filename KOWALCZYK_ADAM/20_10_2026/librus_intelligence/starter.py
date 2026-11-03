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
            raise ValueError(
                f"Unknown column: {col}. Available columns: {', '.join(df.columns)}"
            )

    result = df
    for col, value in filters.items():
        if pd.api.types.is_numeric_dtype(result[col]) and isinstance(value, str):
            # A menu answer always arrives as text, so '5' must become 5 for numeric columns.
            value = pd.to_numeric(value)
        result = result[result[col] == value]
    return result


def summary_by_subject(df: pd.DataFrame) -> pd.DataFrame:
    """Return record count and mean base grade by subject.

    average_base_grade is NOT the official term grade (ocena semestralna):

    * Every record counts the same, while Librus weights categories
      (a sprawdzian counts far more than aktywność or a zadanie domowe).
    * The '+' and '-' modifiers are dropped, so '5+' and '5-' both become 5.
    * All records are pooled together, with no split by semester or term.
    * Grades that the teacher excludes from the average (for example 'np' or
      a grade entered for information only) are not filtered out here.

    Treat the result as a rough picture of the records, not as a prediction.
    """
    return df.groupby("subject").agg(
        record_count=("grade", "count"),
        average_base_grade=("grade_base", "mean")
    ).reset_index()


def parse_filters(raw: str) -> dict[str, str]:
    """Turn 'subject=Matematyka, grade=5' into a dict of column/value pairs."""
    filters: dict[str, str] = {}
    for part in raw.split(","):
        if not part.strip():
            continue
        if "=" not in part:
            raise ValueError(f"Expected column=value, got: {part.strip()}")
        column, value = part.split("=", 1)
        filters[column.strip()] = value.strip()
    if not filters:
        raise ValueError("Provide at least one filter, for example subject=Matematyka")
    return filters


def show(result: pd.DataFrame) -> None:
    """Print a result table, or a clear message when nothing matched."""
    if result.empty:
        print("No grade records match this query.")
    else:
        print(result.to_string(index=False))


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

    print(f"Loaded {len(df)} grade records from grades.csv.")
    print(f"Columns: {', '.join(df.columns)}")
    print("First rows:")
    print(df.head().to_string(index=False))

    while True:
        print("\nLIBRUS INTELLIGENCE")
        print("1. Show grades below a base grade")
        print("2. Search by subject")
        print("3. Search by date range")
        print("4. Report with several filters at once")
        print("5. Summary by subject")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                threshold = float(input("Show base grades below: "))
                show(grades_below(df, threshold))
            elif choice == "2":
                subject = input("Subject name (or part of it): ").strip()
                show(grades_for_subject(df, subject))
            elif choice == "3":
                date_from = input("Date from (YYYY-MM-DD): ").strip()
                date_to = input("Date to (YYYY-MM-DD): ").strip()
                show(grades_between_dates(df, date_from, date_to))
            elif choice == "4":
                print(f"Available columns: {', '.join(df.columns)}")
                raw = input("Filters as column=value, separated by commas: ")
                show(report(df, **parse_filters(raw)))
            elif choice == "5":
                show(summary_by_subject(df))
            elif choice == "6":
                print("Goodbye.")
                break
            else:
                print("Unknown option. Choose 1–6.")
        except ValueError as exc:
            print(f"Invalid input: {exc}")


if __name__ == "__main__":
    main()
