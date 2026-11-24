from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
REQUIRED_COLUMNS = {"date", "subject", "grade", "description"}

def load_grades(path=ROOT / "grades.csv"):
    df = pd.read_csv(path, dtype={"grade": "string", "subject": "string"})
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["subject"] = df["subject"].str.strip()
    df["grade"] = df["grade"].str.strip()
    df["grade_base"] = pd.to_numeric(df["grade"].str.extract(r"^([1-6])[+-]?$", expand=False), errors="coerce")
    return df

def grades_below(df, threshold=3):
    return df.loc[df["grade_base"] < threshold].copy()

def grades_for_subject(df, subject):
    return df.loc[df["subject"].str.contains(subject, case=False, na=False, regex=False)].copy()

def grades_between_dates(df, date_from, date_to):
    start = pd.to_datetime(date_from, format="%Y-%m-%d", errors="raise")
    end = pd.to_datetime(date_to, format="%Y-%m-%d", errors="raise")
    if pd.isna(start) or pd.isna(end) or start > end:
        raise ValueError("Enter valid dates with the start no later than the end.")
    return df.loc[df["date"].between(start, end, inclusive="both")].copy()

def report(df, **filters):
    unknown = set(filters) - set(df.columns)
    if unknown:
        raise ValueError("Unknown columns: " + ", ".join(sorted(unknown)))
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        mask &= df[column].eq(value).fillna(False)
    return df.loc[mask].copy()

def summary_by_subject(df):
    return df.groupby("subject", dropna=False).agg(record_count=("grade", "size"), average_base_grade=("grade_base", "mean")).reset_index()

def multiple_filters(df):
    filters = {}
    print("Exact filters, combined with AND. Columns:", ", ".join(df.columns))
    while True:
        column = input("Column (Enter to run): ").strip()
        if not column:
            return report(df, **filters)
        if column not in df.columns:
            raise ValueError("Unknown column: " + column)
        value = input("Exact value: ").strip()
        if column == "date":
            value = pd.to_datetime(value, format="%Y-%m-%d", errors="raise")
            if pd.isna(value):
                raise ValueError("A date is required.")
        elif column == "grade_base":
            value = float(value)
        filters[column] = value

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Local-only grade exploration")
    parser.add_argument("--csv", type=Path, default=ROOT / "grades.csv")
    args = parser.parse_args()
    try:
        df = load_grades(args.csv)
    except (OSError, ValueError) as exc:
        print("Could not load CSV:", exc)
        print("Create grades.csv locally or use --csv sample_grades.csv for fictional data.")
        return
    if df.empty:
        print("No records found.")
        return
    print(df.head().to_string(index=False))
    print(f"Records: {len(df)}; invalid dates: {df['date'].isna().sum()}; nonnumeric grades: {df['grade_base'].isna().sum()}")
    while True:
        print("\n1 Below base grade\n2 Subject search\n3 Date range\n4 Multiple exact filters\n5 Subject summary\n6 Exit")
        try:
            choice = input("Choose: ").strip()
            if choice == "6":
                break
            if choice == "1":
                result = grades_below(df, float(input("Below: ")))
            elif choice == "2":
                result = grades_for_subject(df, input("Subject: ").strip())
            elif choice == "3":
                result = grades_between_dates(df, input("From YYYY-MM-DD: "), input("To YYYY-MM-DD: "))
            elif choice == "4":
                result = multiple_filters(df)
            elif choice == "5":
                result = summary_by_subject(df)
                print("Simple unweighted base-grade mean, not an official term grade.")
            else:
                print("Choose 1-6.")
                continue
            print(result.to_string(index=False) if not result.empty else "No matching records.")
        except ValueError as exc:
            print("Invalid input:", exc)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

if __name__ == "__main__":
    main()
