"""
DATA RESCUE: The Sales Data Emergency
=====================================
Run:  python analysis.py [path/to/dirty_sales.csv]

Sections
    0. Configuration (every business assumption lives here, in one place)
    1. Mission 1 - profile the damage
    2. Mission 2 - clean_sales()
    3. Mission 3 - add_derived_columns()
    4. Review flags - flag_for_review()
    5. Mission 5 - prepare_sales()
    6. Mission 4 - management questions
    7. Bonus     - quality_report(), benchmark, region x category
    8. main()
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# =============================================================================
# 0. CONFIGURATION
# =============================================================================
REPORT_DATE = pd.Timestamp("2026-10-27")  # "today" for the report. Fixed (not
# Timestamp.now()) so that running the pipeline twice always gives the same result.
VAT_RATE = 0.23
BULK_MIN_QTY = 10
SUSPICIOUS_QTY = 25          # business assumption: >=25 units on one order needs a human look
PRICE_OUTLIER_RATIO = 2.0    # price >2x or <0.5x the product's median price is suspicious
REGION_CODES = {"North": "N", "South": "S", "East": "E", "West": "W"}
TEXT_COLS = ["id", "product", "category", "region", "channel"]
CORE_COLS = ["id", "order_date", "product", "category", "region", "quantity", "price", "channel"]
NUMBER_WORDS = {  # tiny, explicit dictionary: only words we can convert without guessing
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "twelve": 12, "twenty": 20,
}


# =============================================================================
# 1. MISSION 1 - PROFILE THE DAMAGE (works on the RAW frame, never modifies it)
# =============================================================================
def profile_raw(df: pd.DataFrame) -> dict:
    """Print and return a profile of the raw data."""
    print("shape:", df.shape)
    print(df.head(), "\n")
    print("dtypes:\n", df.dtypes, "\n")

    # Real NaN (blank cells) AND "hidden" missing values written as text.
    placeholders = {"", "unknown", "n/a", "na", "none", "null", "-"}
    as_text = df.astype("string").apply(lambda s: s.str.strip().str.lower())
    hidden = as_text.isin(placeholders).sum()
    miss = pd.DataFrame({
        "missing": df.isna().sum(),
        "missing_%": (df.isna().mean() * 100).round(1),
        "placeholder_text": hidden,
    })
    miss["usable_missing_%"] = ((miss["missing"] + miss["placeholder_text"]) / len(df) * 100).round(1)
    print("missing values:\n", miss, "\n")

    n_exact = int(df.duplicated().sum())
    repeated = df["id"][df["id"].duplicated(keep=False)].value_counts()
    print(f"exact duplicate rows: {n_exact}")
    print(f"ids that appear more than once: {repeated.to_dict()}\n")

    uniques = {c: df[c].value_counts(dropna=False).to_dict() for c in ["region", "category", "channel"]}
    for c, v in uniques.items():
        print(f"unique {c}: {v}")
    return {"missing": miss, "exact_duplicates": n_exact, "repeated_ids": repeated, "uniques": uniques}


# =============================================================================
# 2. MISSION 2 - CLEAN THE RAW COLUMNS
# =============================================================================
def _canonical_spelling(s: pd.Series) -> pd.Series:
    """Map every case-variant of a value to its most common spelling in the data.

    Why: product names like 'USB-C Hub' break under .title() ('Usb-C Hub'), and
    hard-coding a product list does not survive new products. Letting the data vote
    keeps casing the business already uses. Ties prefer mixed-case over ALL-CAPS/lower.
    """
    counts = s.value_counts()
    votes = pd.DataFrame({"spelling": counts.index.astype(str), "n": counts.to_numpy()})
    votes["key"] = votes["spelling"].str.lower()
    votes["is_plain"] = (votes["spelling"] == votes["spelling"].str.lower()) | (
        votes["spelling"] == votes["spelling"].str.upper())
    best = (votes.sort_values(["key", "n", "is_plain", "spelling"],
                              ascending=[True, False, True, True])
                 .drop_duplicates("key").set_index("key")["spelling"])
    return s.str.lower().map(best)


def _parse_price(raw: pd.Series) -> pd.Series:
    """Vectorised price parser -> float64 with NaN for anything unusable.

    Handles '$1,299.99', '€ 349,00', '1.299,99', '799.00', '', 'unknown'.
    Rule for separators: if both ',' and '.' appear, the LAST one is the decimal
    mark; a lone ',' is a decimal comma only if followed by 1-2 digits at the end,
    otherwise it is a thousands separator.
    """
    s = raw.astype("string").str.strip().str.lower()
    s = s.str.replace(r"[^\d,.\-]", "", regex=True).fillna("")  # drops $, €, zł, PLN, spaces, 'unknown'...
    has_c, has_d = s.str.contains(",", regex=False), s.str.contains(".", regex=False)
    last_is_comma = s.str.rfind(",") > s.str.rfind(".")
    decimal_comma_only = has_c & ~has_d & s.str.contains(r",\d{1,2}$", regex=True)

    no_commas = s.str.replace(",", "", regex=False)                      # 1,299.99 -> 1299.99
    euro_style = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)  # 1.299,99 -> 1299.99
    obj = lambda x: x.to_numpy(dtype=object)  # np.select wants plain numpy arrays
    out = np.select(
        [obj(has_c & has_d & last_is_comma).astype(bool), obj(decimal_comma_only).astype(bool), obj(has_c).astype(bool)],
        [obj(euro_style), obj(s.str.replace(",", ".", regex=False)), obj(no_commas)],
        default=obj(s),
    )
    price = pd.to_numeric(pd.Series(out, index=raw.index), errors="coerce").astype("float64")
    # A price <= 0 is not a real selling price (free/refund/typo). NaN, never 0.
    return price.where(price > 0)


def _parse_quantity(raw: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return (Int64 quantity, issue label). Invalid quantities become <NA>, never guessed."""
    s = raw.astype("string").str.strip().str.lower()
    from_words = s.map(NUMBER_WORDS)                       # 'five' -> 5 (unambiguous, so we fix it)
    num = pd.to_numeric(s, errors="coerce")
    num = num.where(num.notna(), pd.to_numeric(from_words, errors="coerce")).astype("float64")

    is_blank = s.isna() | (s == "")
    as_bool = lambda x: x.fillna(False).to_numpy(dtype=bool)
    issue = np.select(
        [as_bool(is_blank),
         as_bool(num.isna()),                       # text that is neither number nor known number-word
         as_bool(num < 0),                          # negative: return/refund or sign typo -> cannot be a sale
         as_bool(num == 0),                         # zero-unit order: nothing sold
         as_bool(num != np.floor(num.fillna(0))),   # 2.5 units: not an integer count of items
         as_bool(from_words.notna())],
        ["blank", "non_numeric", "negative", "zero", "non_integer", "converted_from_word"],
        default="",
    )
    issue = pd.Series(issue, index=raw.index, dtype="string").replace("", pd.NA)
    invalid = issue.isin(["blank", "non_numeric", "negative", "zero", "non_integer"]).fillna(False).astype(bool)
    qty = num.where(~invalid).astype("Int64")
    return qty, issue


def clean_sales(df: pd.DataFrame, report_date: pd.Timestamp = REPORT_DATE) -> tuple[pd.DataFrame, dict]:
    """Return (cleaned COPY, report). The input frame is never modified.

    Decisions (also written next to the code):
      * Missing / invalid numbers stay missing (NaN / <NA>) - zero would silently
        pull totals down and look like real data.
      * Rows with bad values are KEPT (not dropped); they are flagged so humans decide.
      * Exact duplicates are dropped (pure double-export, no information lost).
      * Repeated ids with different content: keep the NEWEST order_date, mark
        `id_conflict=True` so a human can confirm. We do not silently pick a winner.
    """
    out = df.copy()  # raw frame stays untouched
    rep: dict = {"rows_in": len(df), "raw_exact_duplicates": int(df.duplicated().sum())}

    # --- 1. strip whitespace --------------------------------------------------
    # Leading/trailing/double spaces make 'north ' != 'north'. Blank strings -> <NA>
    # so "missing" has exactly one representation.
    for c in TEXT_COLS + ["order_date"]:
        raw = out[c].astype("string")
        stripped = raw.str.strip().str.replace(r"\s+", " ", regex=True)
        rep[f"whitespace_fixed_{c}"] = int((raw.notna() & (raw != stripped)).sum())
        out[c] = stripped.mask(stripped.eq("").fillna(False))

    # --- 2. standardise labels ------------------------------------------------
    # Case variants ('NORTH', 'north') are the same business value.
    before = out[["product", "category", "region", "channel"]].copy()
    out["product"] = _canonical_spelling(out["product"])
    for c in ["category", "region", "channel"]:
        out[c] = out[c].str.title()  # these have simple one-word values, title() is safe
    for c in before.columns:
        rep[f"labels_standardised_{c}"] = int((before[c].notna() & (before[c] != out[c])).sum())

    # --- 3. price -> float64 --------------------------------------------------
    raw_price = df["price"].astype("string").str.strip()
    out["price_had_symbol"] = raw_price.str.contains(r"[^\d,.\s\-]", regex=True).fillna(False) & \
        ~raw_price.str.lower().isin(["unknown", "n/a", "na", "none", "null"]).fillna(False)
    out["price"] = _parse_price(df["price"])
    rep["price_missing_blank"] = int((raw_price.isna() | raw_price.eq("")).sum())
    rep["price_missing_placeholder_or_invalid"] = int(out["price"].isna().sum() - rep["price_missing_blank"])
    rep["price_parsed_with_symbol_or_separator"] = int(out["price"].notna().sum() - raw_price.str.fullmatch(r"\d+(\.\d+)?").fillna(False).sum())

    # --- 4. quantity -> Int64 -------------------------------------------------
    # blank / text / zero / negative / fractional -> <NA> + reason in `qty_issue`.
    # Zero & negative are NOT 'fixed' with abs(): -3 could be a return, a typo, or a
    # data-entry sign error; guessing would invent revenue.
    out["quantity"], out["qty_issue"] = _parse_quantity(df["quantity"])
    rep["quantity_issues"] = out["qty_issue"].value_counts().to_dict()
    rep["quantity_set_to_missing"] = int(out["quantity"].isna().sum())

    # --- 5. dates -------------------------------------------------------------
    # Explicit DD.MM.YYYY format: never let pandas guess day/month order.
    # 31.02.2026 does not exist -> NaT (kept as missing, flagged later).
    out["order_date"] = pd.to_datetime(out["order_date"], format="%d.%m.%Y", errors="coerce")
    rep["dates_invalid_or_missing"] = int(out["order_date"].isna().sum())
    rep["dates_in_future"] = int((out["order_date"] > report_date).sum())

    # --- 6. duplicates --------------------------------------------------------
    # Done AFTER standardising so 'north' vs 'North' copies are caught too.
    exact = out.duplicated(subset=CORE_COLS, keep="first")
    out = out.loc[~exact]
    rep["exact_duplicates_dropped"] = int(exact.sum())

    # Same id, different content: keep the newest order_date (NaT counts as oldest;
    # stable sort => later file row wins ties). Missing ids never match each other.
    key = out["id"].astype("object").where(out["id"].notna(), "__missing__" + out.index.astype(str))
    in_conflict = key.duplicated(keep=False)
    order = out.assign(_k=key).sort_values(["_k", "order_date"], kind="stable", na_position="first")
    keep_idx = order.drop_duplicates("_k", keep="last").index
    rep["id_conflicts_resolved"] = int(in_conflict.sum() - key[in_conflict].nunique())
    rep["id_conflict_ids"] = sorted(out.loc[in_conflict, "id"].dropna().unique().tolist())
    out["id_conflict"] = in_conflict
    out = out.loc[out.index.isin(keep_idx)].sort_index()  # original file order, index = raw row position

    rep["rows_out"] = len(out)
    rep["rows_dropped_total"] = rep["rows_in"] - rep["rows_out"]
    rep["remaining_missing"] = {k: int(v) for k, v in out[CORE_COLS].isna().sum().items() if v}
    return out, rep


# =============================================================================
# 3. MISSION 3 - DERIVED COLUMNS (all vectorised, no iterrows)
# =============================================================================
def _label_vectorised(df: pd.DataFrame) -> pd.Series:
    qty = df["quantity"].astype("string").fillna("?")
    return df["product"].astype("string").fillna("?") + " x" + qty


def _label_apply(df: pd.DataFrame) -> pd.Series:
    # Same result via apply(axis=1): correct, but a Python call per row.
    return df.apply(lambda r: f"{r['product'] if pd.notna(r['product']) else '?'} x"
                              f"{r['quantity'] if pd.notna(r['quantity']) else '?'}", axis=1)


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    qty = out["quantity"].astype("float64")          # <NA> -> NaN so arithmetic stays NaN
    # NaN * anything = NaN: missing quantity or price => missing total (NOT zero).
    out["total"] = (qty * out["price"]).round(2)
    out["total_with_vat"] = (out["total"] * (1 + VAT_RATE)).round(2)
    # Nullable boolean: <NA> when quantity is unknown, so "not bulk" and "unknown" differ.
    out["is_bulk"] = out["quantity"] >= BULK_MIN_QTY
    # Missing total is tested FIRST and gets its own label; otherwise it would fall into "low".
    out["priority"] = np.select(
        [out["total"].isna(), out["total"] >= 5000, out["total"] >= 1000],
        ["unknown", "high", "medium"], default="low")
    # Unknown/missing regions -> 'UNK' instead of NaN, so groupbys do not drop them.
    out["region_code"] = out["region"].map(REGION_CODES).fillna("UNK")
    out["product_label"] = _label_vectorised(out)
    return out


# =============================================================================
# 4. REVIEW FLAGS
# =============================================================================
def flag_for_review(df: pd.DataFrame, report_date: pd.Timestamp = REPORT_DATE) -> pd.DataFrame:
    out = df.copy()
    # Compare each price with the MEDIAN of its product (median ignores the outliers
    # themselves). Catches a '$1,299.99' USB-C hub or a 'mouse' priced like headphones.
    med = out.groupby("product")["price"].transform("median")
    ratio = out["price"] / med
    reasons = {
        "invalid_date": out["order_date"].isna(),
        "future_date": (out["order_date"] > report_date).fillna(False),
        "missing_price": out["price"].isna(),
        "invalid_quantity": out["quantity"].isna(),
        "suspicious_quantity": (out["quantity"] >= SUSPICIOUS_QTY).fillna(False).astype(bool),
        "price_outlier": ((ratio > PRICE_OUTLIER_RATIO) | (ratio < 1 / PRICE_OUTLIER_RATIO)).fillna(False),
        "price_currency_symbol": out["price_had_symbol"],
        "id_conflict": out["id_conflict"],
    }
    text = pd.Series("", index=out.index)
    for name, flag in reasons.items():  # loop over 8 COLUMNS (not rows)
        out[f"flag_{name}"] = flag.astype(bool)
        text = text + np.where(flag, name + "; ", "")
    out["review_reasons"] = text.str.rstrip("; ")
    out["needs_review"] = out["review_reasons"] != ""
    return out


# =============================================================================
# 5. MISSION 5 - REPEATABLE PIPELINE
# =============================================================================
def prepare_sales(df: pd.DataFrame, report_date: pd.Timestamp = REPORT_DATE) -> tuple[pd.DataFrame, dict]:
    """clean -> derive -> flag. Pure function: input untouched, deterministic output."""
    cleaned, report = clean_sales(df, report_date)
    result = flag_for_review(add_derived_columns(cleaned), report_date)
    report["orders_needing_review"] = int(result["needs_review"].sum())
    report["totals_missing"] = int(result["total"].isna().sum())
    return result, report


# =============================================================================
# 6. MISSION 4 - MANAGEMENT QUESTIONS
# =============================================================================
def management_answers(df: pd.DataFrame) -> dict:
    ans: dict = {}

    # Q1 - groupby().sum() skips NaN, so incomplete orders add nothing (not zero-filled guesses).
    by_cat = df.groupby("category")["total"].sum().sort_values(ascending=False)
    ans["q1_category_totals"] = by_cat
    print("\nQ1 category totals:\n", by_cat.round(2))

    # Q2
    top5 = df.nlargest(5, "total")[["id", "product", "quantity", "price", "total", "review_reasons"]]
    ans["q2_top5"] = top5
    print("\nQ2 top-5 orders:\n", top5)

    # Q3 - counts orders AFTER duplicate removal
    by_region = df["region"].value_counts()
    ans["q3_region_orders"] = by_region
    print("\nQ3 orders per region:\n", by_region)

    # Q4
    miss_p, miss_q = df["price"].isna(), df["quantity"].isna()
    ans["q4_missing_price_or_qty"] = int((miss_p | miss_q).sum())
    ans["q4_breakdown"] = {"price_only": int((miss_p & ~miss_q).sum()),
                           "quantity_only": int((~miss_p & miss_q).sum()),
                           "both": int((miss_p & miss_q).sum())}
    print("\nQ4 orders without usable price or quantity:", ans["q4_missing_price_or_qty"], ans["q4_breakdown"])

    # Q5
    ans["q5_total"] = float(df["total"].sum())
    ans["q5_orders_counted"] = int(df["total"].notna().sum())
    ans["q5_orders_excluded"] = int(df["total"].isna().sum())
    clean_only = df.loc[~df["needs_review"], "total"].sum()
    ans["q5_total_excluding_review"] = float(clean_only)
    # Indicative gap only (NOT in the headline): missing-price orders priced at the product median.
    med = df.groupby("product")["price"].transform("median")
    gap = (df["quantity"].astype("float64") * med).where(df["price"].isna()).sum()
    ans["q5_indicative_missing_price_value"] = float(gap)
    print(f"\nQ5 total sales (missing totals excluded, not zero-filled): {ans['q5_total']:,.2f} "
          f"from {ans['q5_orders_counted']} orders; {ans['q5_orders_excluded']} orders have no total.")
    print(f"   total from orders with NO review flag at all: {clean_only:,.2f}")
    print(f"   indicative value of missing-price orders (qty x product median): {gap:,.2f}")

    # Q6
    review = df.loc[df["needs_review"], ["id", "order_date", "product", "quantity", "price", "total", "review_reasons"]]
    ans["q6_review"] = review
    print(f"\nQ6 orders for manual review: {len(review)} of {len(df)}")
    print(review.to_string())
    return ans


# =============================================================================
# 7. BONUS
# =============================================================================
def quality_report(df: pd.DataFrame) -> dict:
    """dtypes, missing %, unique values, duplicates, numeric ranges, IQR outliers."""
    num = df.select_dtypes("number")
    q1, q3 = num.quantile(0.25), num.quantile(0.75)
    iqr = q3 - q1
    outliers = ((num < q1 - 1.5 * iqr) | (num > q3 + 1.5 * iqr)).sum()
    return {
        "dtypes": df.dtypes.astype(str),
        "missing_%": (df.isna().mean() * 100).round(1),
        "unique_counts": df.nunique(),
        "exact_duplicate_rows": int(df.duplicated(subset=[c for c in CORE_COLS if c in df]).sum()),
        "repeated_ids": int(df["id"].duplicated().sum()) if "id" in df else None,
        "numeric_ranges": num.agg(["min", "median", "max"]).T,
        "iqr_outlier_counts": outliers,
    }


def benchmark(clean: pd.DataFrame, n: int = 100_000) -> pd.DataFrame:
    """Vectorised vs apply(axis=1) on n rows."""
    big = clean.sample(n, replace=True, random_state=0).reset_index(drop=True)
    rows = []
    for name, fast, slow in [
        ("total", lambda d: d["quantity"].astype("float64") * d["price"],
                  lambda d: d.apply(lambda r: r["quantity"] * r["price"], axis=1)),
        ("product_label", _label_vectorised, _label_apply),
    ]:
        t = time.perf_counter(); a = fast(big); tv = time.perf_counter() - t
        t = time.perf_counter(); b = slow(big); ta = time.perf_counter() - t
        rows.append({"transformation": name, "vectorised_s": round(tv, 4), "apply_s": round(ta, 4),
                     "speedup_x": round(ta / tv, 1)})
    return pd.DataFrame(rows)


def region_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(["region", "category"])
              .agg(orders=("id", "size"), total_sales=("total", "sum"), orders_without_total=("total", lambda s: s.isna().sum()))
              .round(2))


# =============================================================================
# 8. MAIN
# =============================================================================
def main(path: str = "dirty_sales.csv") -> None:
    pd.set_option("display.width", 200, "display.max_columns", 30)
    raw = pd.read_csv(path)
    snapshot = raw.copy()

    print("=" * 30, "MISSION 1: PROFILE", "=" * 30)
    profile_raw(raw)

    print("\n" + "=" * 30, "MISSIONS 2, 3, 5: PIPELINE", "=" * 30)
    result, report = prepare_sales(raw)
    for k, v in report.items():
        print(f"  {k}: {v}")
    assert raw.equals(snapshot), "raw data was modified!"
    twice, _ = prepare_sales(raw)
    assert result.equals(twice), "pipeline is not repeatable!"
    assert _label_vectorised(result).equals(_label_apply(result).astype("string")), "label variants disagree"
    print("  checks passed: raw unchanged, pipeline repeatable, vectorised == apply")

    print("\n" + "=" * 30, "MISSION 4: MANAGEMENT QUESTIONS", "=" * 30)
    management_answers(result)

    print("\n" + "=" * 30, "BONUS", "=" * 30)
    qr = quality_report(result)
    for k in ["missing_%", "numeric_ranges", "iqr_outlier_counts"]:
        print(f"\n{k}:\n{qr[k]}")
    print("\nbenchmark (100,000 rows):\n", benchmark(result))
    print("\nregion x category:\n", region_category_summary(result))

    out_dir = Path(path).resolve().parent
    result.to_csv(out_dir / "clean_sales.csv")
    result[result["needs_review"]].to_csv(out_dir / "review_queue.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dirty_sales.csv")
