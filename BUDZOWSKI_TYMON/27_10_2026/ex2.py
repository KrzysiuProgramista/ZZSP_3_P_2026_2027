from pprint import pprint

import pandas as pd


def quality_report(df: pd.DataFrame, z: float = 3.0, cat_threshold: int = 20) -> dict:
    """Profil jakości dowolnego DataFrame. Nie modyfikuje wejścia. Zwraca dict."""
    n = len(df)
    columns = {}
    for col in df.columns:
        s = df[col]
        nunique = int(s.nunique(dropna=True))
        info = {
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "missing_pct": round(float(s.isna().mean()) * 100, 1) if n else 0.0,
            "unique": nunique,
        }
        if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
            x = s.dropna()
            if len(x):
                std = x.std()
                info["min"] = float(x.min())
                info["max"] = float(x.max())
                info["mean"] = round(float(x.mean()), 2)
                info["outliers"] = int(((x - x.mean()).abs() > z * std).sum()) if std and std > 0 else 0
        warnings = []
        if n and nunique <= 1:
            warnings.append("constant")
        if n and nunique == n and s.notna().all():
            warnings.append("possible ID")
        if (s.dtype == object or pd.api.types.is_string_dtype(s)) and 0 < nunique < cat_threshold:
            warnings.append("consider category")
        if n and info["missing"] == n:
            warnings.append("all missing")
        info["warnings"] = warnings
        columns[col] = info

    return {
        "rows": n,
        "columns": df.shape[1],
        "duplicate_rows": int(df.duplicated().sum()),
        "per_column": columns,
    }


if __name__ == "__main__":
    raw = pd.read_csv("dirty_data.csv")

    typed = raw.copy()
    typed["price"] = pd.to_numeric(
        typed["price"].astype("string").str.replace(r"[\s$€,]", "", regex=True),
        errors="coerce")
    typed["quantity"] = pd.to_numeric(typed["quantity"], errors="coerce").astype("Int64")
    typed["order_date"] = pd.to_datetime(typed["order_date"], format="%d.%m.%Y", errors="coerce")

    pprint(quality_report(typed), sort_dicts=False)