import pandas as pd
import numpy as np


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Create a reusable quality profile for any DataFrame."""

    rows = []

    for column in df.columns:
        series = df[column]

        row = {
            "column": column,
            "dtype": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_percent": round(series.isna().mean() * 100, 2),
            "unique_count": int(series.nunique(dropna=True)),
        }

        # Numeric statistics
        if pd.api.types.is_numeric_dtype(series):
            mean = series.mean()
            std = series.std()

            outliers = 0
            if pd.notna(mean) and pd.notna(std) and std != 0:
                outliers = int(
                    ((series - mean).abs() > 3 * std).sum()
                )

            row.update({
                "min": series.min(),
                "max": series.max(),
                "mean": round(mean, 2) if pd.notna(mean) else None,
                "outlier_count": outliers,
            })
        else:
            row.update({
                "min": None,
                "max": None,
                "mean": None,
                "outlier_count": None,
            })

        # Warnings
        warnings = []

        if row["unique_count"] <= 1:
            warnings.append("constant column")

        if row["unique_count"] == len(df):
            warnings.append("possible identifier")

        if (
            pd.api.types.is_object_dtype(series)
            and row["unique_count"] < 20
        ):
            warnings.append("consider category dtype")

        row["warnings"] = ", ".join(warnings) if warnings else ""
        rows.append(row)

    report = pd.DataFrame(rows)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print()

    return report


# Test it on the sales dataset
data = {
    "date": [
        "2026-01-05", "2026-01-07", "2026-01-12", "2026-01-15",
        "2026-01-19", "2026-02-02", "2026-02-08", "2026-02-14",
        "2026-02-21", "2026-03-03", "2026-03-11", "2026-03-18",
        "2026-03-25", "2026-04-02", "2026-04-09", "2026-04-16",
        "2026-04-23", "2026-05-04"
    ],
    "product": [
        "Laptop", "Mouse", "Desk", "Laptop", "Chair", "Monitor",
        "Desk", "Mouse", "Laptop", "Chair", "Monitor", "Keyboard",
        "Desk", "Laptop", "Chair", "Keyboard", "Monitor", "Desk"
    ],
    "category": [
        "Electronics", "Electronics", "Furniture", "Electronics",
        "Furniture", "Electronics", "Furniture", "Electronics",
        "Electronics", "Furniture", "Electronics", "Electronics",
        "Furniture", "Electronics", "Furniture", "Electronics",
        "Electronics", "Furniture"
    ],
    "region": [
        "North", "North", "South", "South", "North", "East",
        "East", "West", "West", "South", "North", "East",
        "West", "North", "East", "South", "West", "North"
    ],
    "quantity": [3, 25, 5, 2, 12, 8, 3, 40, 1, 20, 4, 15, 7, 5, 9, 30, 6, 2],
    "unit_price": [
        3500.00, 45.00, 890.00, 3500.00, 450.00, 1200.00,
        890.00, 45.00, 3500.00, 450.00, 1200.00, 199.00,
        890.00, 3500.00, 450.00, 199.00, 1200.00, 890.00
    ],
}

df = pd.DataFrame(data)

report = quality_report(df)
print(report)