import pandas as pd
import numpy as np

def quality_report(df, z_threshold=3):
    n_rows = len(df)
    columns = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing": df.isna().sum(),
        "missing_pct": (df.isna().mean() * 100).round(1),
        "unique": df.nunique(dropna=True),
    })

    num = df.select_dtypes(include="number")
    numeric = pd.DataFrame({
        "min": num.min(),
        "max": num.max(),
        "mean": num.mean().round(2),
    })
    std = num.std().replace(0, np.nan)        
    z = (num - num.mean()) / std
    numeric["outliers"] = (z.abs() > z_threshold).sum()

    warnings = []
    for col, row in columns.iterrows():
        s = df[col]
        if row["unique"] <= 1:
            warnings.append(f"{col}: constant column, probably not useful for analysis")
        if row["unique"] == n_rows and n_rows > 0:
            warnings.append(f"{col}: unique value in every row, possibly an identifier")
        if (pd.api.types.is_string_dtype(s) and 1 < row["unique"] < 20):
            warnings.append(
                f"{col}: text column with {row['unique']} unique values, consider category dtype"
            )
    return {
        "columns": columns,
        "numeric": numeric,
        "duplicate_rows": int(df.duplicated().sum()),
        "warnings": warnings,
    }



df = pd.read_csv("/Users/programista/Documents/Python/ZZSP_3_P_2026_2027/TUTKEVYCH_VOLODYMYR/27_10_2026/dirty_data.csv")

report_staff = quality_report(df)
print(report_staff["columns"])
print(report_staff["numeric"])
print(report_staff["warnings"])
