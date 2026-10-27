import pandas as pd


def quality_report(df: pd.DataFrame, z: float = 3.0, cat_threshold: int = 20):
    n = len(df)
    rows = []
    for col in df.columns:
        s = df[col]
        nunique = s.nunique(dropna=True)
        r = {
            "column": col,
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "missing_pct": round(s.isna().mean() * 100, 1) if n else 0.0,
            "unique": int(nunique),
            "min": None, "max": None, "mean": None, "outliers": None,
            "warnings": [],
        }
        if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
            x = s.dropna()
            if len(x):
                r["min"], r["max"], r["mean"] = x.min(), x.max(), round(x.mean(), 2)
                std = x.std()
                r["outliers"] = int(((x - x.mean()).abs() > z * std).sum()) if std and std > 0 else 0
        if n and nunique <= 1:
            r["warnings"].append("constant")
        if n and nunique == n and s.notna().all():
            r["warnings"].append("possible ID")
        if s.dtype == object or pd.api.types.is_string_dtype(s):
            if 0 < nunique < cat_threshold:
                r["warnings"].append("consider category")
        if r["missing"] == n and n:
            r["warnings"].append("all missing")
        r["warnings"] = ", ".join(r["warnings"])
        rows.append(r)

    columns = pd.DataFrame(rows).set_index("column")
    dataset = {
        "rows": n,
        "columns": df.shape[1],
        "duplicate_rows": int(df.duplicated().sum()),
    }
    return columns, dataset


def print_report(df, title):
    cols, ds = quality_report(df)
    print(f"\n=== {title} ===")
    print(ds)
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(cols.fillna("").to_string())


if __name__ == "__main__":
    raw = pd.read_csv("dirty_data.csv")
    before = raw.copy(deep=True)

    print_report(raw, "RAW dirty_data.csv")

    typed = raw.copy()
    typed["price"] = pd.to_numeric(
        typed["price"].astype("string").str.replace(r"[\s$€,]", "", regex=True),
        errors="coerce")
    typed["quantity"] = pd.to_numeric(typed["quantity"], errors="coerce").astype("Int64")
    typed["order_date"] = pd.to_datetime(typed["order_date"], format="%d.%m.%Y", errors="coerce")
    print_report(typed, "TYPED (price/quantity/date sparsowane)")

    pd.testing.assert_frame_equal(raw, before)  

    print("\nRepeated ids:", typed.loc[typed["id"].duplicated(keep=False), "id"].unique().tolist())
    print("Region raw values:", sorted(raw["region"].dropna().map(repr).unique()))
    print("Future dates:", typed.loc[typed["order_date"] > pd.Timestamp.today().normalize(), ["id", "order_date"]].to_dict("records"))
    print("Negative qty:", typed.loc[typed["quantity"] < 0, ["id", "quantity"]].to_dict("records"))
    p = typed["price"]
    print("Price z-scores top:", ((p - p.mean()) / p.std()).abs().round(2).nlargest(3).to_dict())