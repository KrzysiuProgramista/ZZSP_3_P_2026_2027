import numpy as np
import pandas as pd

OUTLIER_SIGMA = 3
CATEGORY_HINT_MAX_UNIQUE = 20
TEXT_PATTERN_MIN_SHARE = 0.80
ID_HINT_MIN_ROWS = 10

DATE_LIKE = r"^\s*\d{1,4}[-./]\d{1,2}[-./]\d{1,4}"

PER_COLUMN_ORDER = [
    "column", "dtype", "missing", "missing_pct", "unique",
    "min", "max", "mean", "outliers_3sd",
]


def _numeric_like_share(series):
    present = series.dropna()
    if present.empty:
        return 0.0
    text = (present.astype("string")
            .str.strip()
            .str.replace(r"[\s ]", "", regex=True)
            .str.replace(r"[$€,]", "", regex=True))
    return float(pd.to_numeric(text, errors="coerce").notna().mean())


def _date_like_share(series):
    present = series.dropna()
    if present.empty:
        return 0.0
    text = present.astype("string")
    return float(text.str.match(DATE_LIKE, na=False).mean())


def _outlier_count(series):
    present = series.dropna()
    if len(present) < 3:
        return 0
    std = present.std()
    if pd.isna(std) or std == 0:
        return 0
    return int(((present - present.mean()).abs() > OUTLIER_SIGMA * std).sum())


def quality_report(df, name="dataset"):
    n_rows = len(df)
    rows = []
    warnings = []

    for column in df.columns:
        series = df[column]
        missing = int(series.isna().sum())
        unique = int(series.nunique(dropna=True))

        is_numeric = (pd.api.types.is_numeric_dtype(series)
                      and not pd.api.types.is_bool_dtype(series))
        is_datetime = pd.api.types.is_datetime64_any_dtype(series)

        row = {
            "column": column,
            "dtype": str(series.dtype),
            "missing": missing,
            "missing_pct": round(missing / n_rows * 100, 1) if n_rows else 0.0,
            "unique": unique,
            "min": pd.NA, "max": pd.NA, "mean": pd.NA, "outliers_3sd": pd.NA,
        }
        if is_numeric:
            present = series.dropna()
            if not present.empty:
                row["min"] = round(float(present.min()), 2)
                row["max"] = round(float(present.max()), 2)
                row["mean"] = round(float(present.mean()), 2)
            row["outliers_3sd"] = _outlier_count(series)
        rows.append(row)

        if n_rows and missing == n_rows:
            warnings.append(f"{column!r}: completely empty (100% missing)")
            continue
        if n_rows and unique <= 1:
            warnings.append(
                f"{column!r}: constant column (1 unique value)"
                f" - likely not useful for analysis")
            continue
        if (unique == n_rows and missing == 0
                and n_rows >= ID_HINT_MIN_ROWS
                and not pd.api.types.is_float_dtype(series)):
            warnings.append(
                f"{column!r}: unique in every row - possibly an identifier")

        if is_numeric or is_datetime:
            continue

        if _numeric_like_share(series) >= TEXT_PATTERN_MIN_SHARE:
            warnings.append(
                f"{column!r}: stored as {series.dtype} but"
                f" {_numeric_like_share(series):.0%} of values parse as"
                f" numbers - convert with pd.to_numeric before arithmetic")
        elif _date_like_share(series) >= TEXT_PATTERN_MIN_SHARE:
            warnings.append(
                f"{column!r}: stored as {series.dtype} but looks like a date"
                f" - parse it with pd.to_datetime(..., format=...)")
        else:
            normalised = int(series.dropna().astype("string")
                             .str.strip().str.lower().nunique())
            if normalised < unique:
                warnings.append(
                    f"{column!r}: {unique} unique values collapse to"
                    f" {normalised} after strip + lower - inconsistent"
                    f" casing or whitespace creates false categories")
            if 1 < normalised < CATEGORY_HINT_MAX_UNIQUE:
                warnings.append(
                    f"{column!r}: only {unique} unique values"
                    f" - consider category dtype")

    per_column = pd.DataFrame(rows, columns=PER_COLUMN_ORDER)

    duplicate_rows = int(df.duplicated().sum()) if n_rows else 0
    if duplicate_rows:
        warnings.append(f"{duplicate_rows} fully duplicated row(s)")

    return {
        "name": name,
        "rows": n_rows,
        "columns": df.shape[1],
        "duplicate_rows": duplicate_rows,
        "complete_rows": int(df.notna().all(axis=1).sum()) if n_rows else 0,
        "rows_with_any_gap": int(df.isna().any(axis=1).sum()) if n_rows else 0,
        "per_column": per_column,
        "warnings": warnings,
    }


def print_quality_report(report):
    print("=" * 78)
    print(f"QUALITY REPORT - {report['name']}")
    print("=" * 78)
    print(f"rows: {report['rows']}   columns: {report['columns']}   "
          f"duplicate rows: {report['duplicate_rows']}")
    print(f"complete rows: {report['complete_rows']}   "
          f"rows with at least one gap: {report['rows_with_any_gap']}")

    print("\nper column:")
    if report["per_column"].empty:
        print("  (no columns)")
    else:
        print(report["per_column"].to_string(index=False, na_rep="-"))

    print(f"\nwarnings ({len(report['warnings'])}):")
    if not report["warnings"]:
        print("  none")
    for warning in report["warnings"]:
        print(f"  ! {warning}")
    print()


def edge_case_frame():
    score = [10.0, 9.5, 11.0, 10.5, 9.0, 10.2, 9.8, 10.7, 9.3, 10.1,
             10.4, 9.6, 10.9, 9.1, 10.3, 9.9, 10.6, 9.4, 10.8, 9.2,
             10.0, 9.7, 11.0, 9.5, 60.0]
    return pd.DataFrame({
        "record_id": np.arange(1, 26),
        "currency": ["PLN"] * 25,
        "notes": [None] * 25,
        "amount_text": ["1 200.00", "350.00", "99.50"] * 8 + ["7 400.00"],
        "signed_on": ["0%d.0%d.2026" % (d % 9 + 1, d % 9 + 1)
                      for d in range(25)],
        "status": (["open", "closed"] * 13)[:25],
        "score": score,
    })


def main():
    dirty = pd.read_csv("dirty_data.csv")
    employees = pd.read_csv("employees.csv")
    edge = edge_case_frame()

    before_dirty = dirty.copy(deep=True)

    for frame, label in [
        (dirty, "dirty_data.csv"),
        (employees, "employees.csv"),
        (edge, "edge_case_frame (synthetic, 25 rows)"),
    ]:
        print_quality_report(quality_report(frame, label))

    pd.testing.assert_frame_equal(dirty, before_dirty)

    print_quality_report(quality_report(pd.DataFrame(), "empty DataFrame"))

    print("Do the warnings make sense in context?")
    print()
    print("dirty_data.csv")
    print("  Useful: 'price' really is text - '3 500.00' uses a space as the")
    print("  thousands separator, so pandas refuses to make it numeric.")
    print("  'order_date' is flagged as an unparsed date (dd.mm.yyyy).")
    print("  One fully duplicated row (id 10) is real. 'quantity' shows one")
    print("  3-sigma outlier: the -40 that cannot be a real quantity.")
    print("  'region' is caught too: 7 labels collapse to 4 once you strip")
    print("  and lowercase them ('North', 'north', ' North ', 'NORTH').")
    print("  'id' is correctly NOT called an identifier - id 10 repeats.")
    print("  What the report CANNOT see yet: the 99 999.00 price in row 14.")
    print("  While 'price' is text there are no numeric stats, so that")
    print("  outlier only becomes visible after clean(df) converts the dtype.")
    print()
    print("employees.csv")
    print("  Mostly clean, and the report says so: no gaps, no duplicates,")
    print("  no outliers. 'department' (4 values) gets the category hint,")
    print("  which is genuinely worth acting on.")
    print("  FALSE POSITIVE worth discussing: 'last_name' is flagged as a")
    print("  possible identifier only because 20 people happen to have 20")
    print("  different surnames. Uniqueness is weak evidence on small data.")
    print()
    print("edge_case_frame (synthetic)")
    print("  Every warning fires as designed: constant 'currency', empty")
    print("  'notes', identifier 'record_id', numeric-looking 'amount_text',")
    print("  date-looking 'signed_on', and the 60.0 in 'score' is caught as a")
    print("  3-sigma outlier because the frame is big enough for the rule to")
    print("  work at all.")


if __name__ == "__main__":
    main()
