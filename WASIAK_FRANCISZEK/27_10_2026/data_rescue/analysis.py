"""Data Rescue - analysis.py  (run: python analysis.py)"""
import numpy as np
import pandas as pd

TODAY = pd.Timestamp("2026-11-03")          # fixed "report date" => deterministic runs
REGION_CODES = {"North": "N", "South": "S", "East": "E", "West": "W"}


def parse_price(s: pd.Series) -> pd.Series:
    """Vectorised price parser: '$1,299.99', '€ 349,00', 'unknown', '' -> float/NaN."""
    t = s.astype("string").str.strip().str.lower()
    t = t.str.replace(r"[^\d,.\-]", "", regex=True)          # drop symbols/spaces/words ('unknown' -> '')
    both = t.str.contains(",", na=False) & t.str.contains(r"\.", na=False)
    only_comma = t.str.contains(",", na=False) & ~both
    t = t.mask(both, t.str.replace(",", "", regex=False))     # 1,299.99 -> comma = thousands
    t = t.mask(only_comma, t.str.replace(",", ".", regex=False))  # 349,00 -> comma = decimal
    t = t.replace("", pd.NA)                                  # blank/unknown stays missing, never 0
    out = pd.to_numeric(t, errors="coerce").astype("float64")
    return out.mask(out <= 0)                                 # a price <= 0 is impossible -> NaN


def clean_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return a cleaned copy and a report of cleaning actions."""
    out = df.copy(deep=True)                                  # raw frame must stay untouched
    rep = {"rows_in": len(df)}
    for c in ["id", "product", "category", "region", "channel"]:
        out[c] = out[c].astype("string").str.strip()          # stray spaces break grouping
    out["id"] = out["id"].str.upper()
    out["product"] = out["product"].str.replace(r"\s+", " ", regex=True)
    key = out["product"].str.lower()
    canon = out.groupby(key)["product"].agg(lambda s: s.value_counts().index[0])
    rep["product_fixed"] = int((out["product"] != key.map(canon)).sum())
    out["product"] = key.map(canon)
    out["region"] = out["region"].str.title()
    out["channel"] = out["channel"].str.title()
    # category: the same product can't be in two categories -> trust product's majority category
    cat_raw = out["category"].str.title()
    prod_cat = cat_raw.groupby(out["product"]).agg(lambda s: s.mode().iat[0])
    out["category"] = out["product"].map(prod_cat).fillna(cat_raw)
    rep["category_fixed"] = int((out["category"] != cat_raw).sum()) + int((cat_raw != df["category"].astype("string")).sum())
    # price
    p = parse_price(out["price"])
    raw_p = out["price"].astype("string").str.strip()
    rep["price_set_to_nan"] = int((p.isna() & raw_p.notna() & (raw_p != "")).sum())
    rep["price_blank"] = int((raw_p.isna() | (raw_p == "")).sum())
    rep["price_reformatted"] = int(p.notna().sum() - pd.to_numeric(raw_p, errors="coerce").notna().sum())
    out["price"] = p
    out["price_foreign_symbol"] = raw_p.str.contains(r"[€$]", na=False)  # currency never converted -> flag
    # quantity: non-numeric/0/negative are not valid sales; NaN (not 0) keeps them visible
    q = pd.to_numeric(out["quantity"], errors="coerce")
    q = q.where(q.notna() & (q == q.round()) & (q > 0))
    rep["quantity_invalid"] = int(q.isna().sum() - out["quantity"].isna().sum() - (out["quantity"].astype("string").str.strip() == "").sum())
    out["quantity"] = q.astype("Int64")
    # dates
    d = pd.to_datetime(out["order_date"].astype("string").str.strip(), format="%d.%m.%Y", errors="coerce")
    rep["date_invalid"] = int(d.isna().sum())
    out["order_date"] = d
    out["date_future"] = d > TODAY                            # future order in a historical report
    # duplicates
    before = len(out)
    out = out.drop_duplicates()                               # exact duplicates add no information
    rep["exact_duplicates_dropped"] = before - len(out)
    dup_mask = out.duplicated("id", keep=False)
    out["id_conflict"] = dup_mask                             # same id, different content: flag it
    rep["conflicting_id_rows"] = int(dup_mask.sum())
    out = out.sort_values(["id", "order_date"], kind="stable")
    n = len(out)
    out = out.drop_duplicates("id", keep="last")              # keep newest record per id
    rep["conflict_older_dropped"] = n - len(out)
    out = out.reset_index(drop=True)
    med = out.groupby("product")["price"].transform("median")
    out["price_outlier"] = (out["price"] > 3 * med) | (out["price"] < med / 3)
    rep["rows_out"] = len(out)
    rep["remaining_missing"] = out[["order_date", "quantity", "price"]].isna().sum().astype(int).to_dict()
    return out, rep


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["total"] = out["quantity"].astype("Float64") * out["price"]      # NaN if either missing
    out["total_with_vat"] = out["total"] * 1.23
    out["is_bulk"] = (out["quantity"] >= 10).fillna(False).astype(bool)
    t = out["total"].astype("float64")
    out["priority"] = np.select([t >= 5000, t >= 1000, t < 1000], ["high", "medium", "low"], default="unknown")
    out["region_code"] = out["region"].map(REGION_CODES).fillna("UNK")
    out["product_label"] = out["product"] + " x" + out["quantity"].astype("string").fillna("?")
    out["needs_review"] = (out["order_date"].isna() | out["date_future"] | out["quantity"].isna()
                           | out["price"].isna() | out["id_conflict"] | out["price_outlier"]
                           | out["price_foreign_symbol"] | (out["quantity"] > 20).fillna(False))
    return out


def prepare_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    cleaned, rep = clean_sales(df)
    return add_features(cleaned), rep


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes("number")
    return pd.DataFrame({"dtype": df.dtypes.astype(str), "missing_%": (df.isna().mean() * 100).round(1),
                         "unique": df.nunique()}).join(num.agg(["min", "max"]).T)


if __name__ == "__main__":
    raw = pd.read_csv("dirty_sales.csv", dtype=str)
    snap = raw.copy()
    print("== 1. PROFILE ==")
    print(raw.shape); print(raw.dtypes)
    print(raw.isna().sum().to_frame("missing").assign(pct=(raw.isna().mean() * 100).round(1)))
    print("exact dups:", raw.duplicated().sum(), "| repeated ids:", raw["id"].duplicated(keep=False).sum())
    for c in ["region", "category", "channel"]:
        print(c, sorted(raw[c].dropna().unique().tolist()))
    df, rep = prepare_sales(raw)
    assert raw.equals(snap)
    print("== REPORT =="); print(rep)
    print("== Q1 category totals =="); print(df.groupby("category")["total"].sum().sort_values(ascending=False))
    print("== Q2 top 5 =="); print(df.nlargest(5, "total")[["id", "product_label", "region", "total"]])
    print("== Q3 orders per region =="); print(df["region"].value_counts())
    print("== Q4 =="); print("missing price:", df.price.isna().sum(), "missing qty:", df.quantity.isna().sum(),
                              "either:", (df.price.isna() | df.quantity.isna()).sum())
    print("== Q5 total =="); print(round(df["total"].sum(), 2), "complete rows:", df.total.notna().sum(), "of", len(df))
    print("== Q6 review =="); print(df.needs_review.sum()); print(df[df.needs_review][["id","order_date","quantity","price","id_conflict","price_outlier","price_foreign_symbol","date_future"]].to_string())
    print("== BONUS group =="); print(df.groupby(["region","category"]).agg(sales=("total","sum"), orders=("id","count")).round(0))
    import time
    big = pd.concat([df] * 1000, ignore_index=True).head(100_000)
    t0 = time.perf_counter(); a = big["product"] + " x" + big["quantity"].astype("string").fillna("?"); t1 = time.perf_counter()
    b = big.apply(lambda r: f"{r['product']} x{r['quantity'] if pd.notna(r['quantity']) else '?'}", axis=1); t2 = time.perf_counter()
    print(f"bench vectorised {t1-t0:.3f}s vs apply {t2-t1:.3f}s; equal={a.tolist()==b.tolist()}")
    df.to_csv("clean_sales.csv", index=False)
