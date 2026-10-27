import pandas as pd
import numpy as np

df = pd.read_csv('dirty.csv')

def cleanup(df):
    df = df.drop_duplicates().copy()

    for col in df.select_dtypes(include=["object", "string"]).columns:
        if col != "order_date":
            df[col] = df[col].astype(str).str.strip().str.title()
            df[col] = df[col].replace("Nan", np.nan)

    if "price" in df.columns:
        df["price"] = (
            df["price"].astype(str).str.replace(" ", "").replace("Nan", np.nan)
        )
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    return df

def quality_report(df):
    total_rows = len(df)
    dtypes = df.dtypes
    missing_counts = df.isnull().sum()
    missing_pcts = (missing_counts / total_rows) * 100
    unique_counts = df.nunique()

    numeric_df = df.select_dtypes(include=[np.number])
    mins = numeric_df.min()
    maxs = numeric_df.max()
    means = numeric_df.mean()
    stds = numeric_df.std()
    outliers = pd.Series(0, index=df.columns)

    for col in numeric_df.columns:
        s = df[col].dropna()
    if len(s) > 0 and stds[col] > 0:
        outliers[col] = (abs(s - means[col]) > 3 * stds[col]).sum()

    report = pd.DataFrame({
        "dtype": dtypes,
        "missing_count": missing_counts,
        "missing_pct": missing_pcts.map("{:.1f}%".format),
        "unique_count": unique_counts,
        "min": mins,
        "max": maxs,
        "mean": means.round(2),
        "outliers_3std": outliers,
    })

    return report

report = quality_report(df)
print(cleanup(df))
print(report.fillna("-"))

