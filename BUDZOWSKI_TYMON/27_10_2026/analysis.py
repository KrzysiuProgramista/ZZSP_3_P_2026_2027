from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration (all cleaning decisions are driven from here)
# ---------------------------------------------------------------------------
VAT_RATE = 0.23
BULK_QTY = 10
SUSPICIOUS_QTY = 20            # orders this large are plausible but worth a human look
PRICE_OUTLIER_RATIO = (0.5, 2.0)  # price outside 0.5x–2x the product median → suspicious
REPORT_CUTOFF = pd.Timestamp("2026-10-31")  # end of the reporting period; later dates are "future"
BASE_CURRENCY = "PLN"          # 23% VAT → Polish report; unmarked prices assumed PLN

TEXT_COLS = ["id", "order_date", "product", "category", "region", "quantity", "price", "channel"]
MISSING_TOKENS = {"", "unknown", "n/a", "na", "nan", "none", "null", "-"}

# Canonical spellings; lookup is case/whitespace-insensitive.
CANONICAL_PRODUCTS = [
    "Office Chair", "Laptop Pro 14", "Wireless Mouse", "Notebook Pack", "Webcam HD",
    "Mechanical Keyboard", "Monitor 27", "Headphones", "USB-C Hub", "Desk Lamp",
    "Standing Desk", "Whiteboard",
]
PRODUCT_LOOKUP = {p.lower(): p for p in CANONICAL_PRODUCTS}
REGION_CODES = {"North": "N", "South": "S", "East": "E", "West": "W"}
UNKNOWN_REGION_CODE = "UNK"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _norm_key(s: pd.Series) -> pd.Series:
    """Lower-case, trimmed, single-spaced key used for matching variants."""
    return s.str.strip().str.replace(r"\s+", " ", regex=True).str.lower()


def _parse_price(raw: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return (numeric price, currency code). Invalid/missing → NaN, never 0."""
    s = raw.str.strip()
    missing = s.isna() | s.str.lower().isin(MISSING_TOKENS)

    # Currency is detected, not converted: no FX rate is given, so converting would
    # invent numbers. The currency is kept so foreign prices can be flagged for review.
    currency = pd.Series(
        np.select(
            [s.str.contains("$", regex=False, na=False), s.str.contains("€", regex=False, na=False)],
            ["USD", "EUR"],
            default=BASE_CURRENCY,
        ),
        index=raw.index,
    ).where(~missing)

    digits = s.str.replace(r"[^\d,.\-]", "", regex=True)
    has_comma = digits.str.contains(",", regex=False, na=False)
    has_dot = digits.str.contains(".", regex=False, na=False)
    comma_is_thousands = digits.str.fullmatch(r"-?\d{1,3}(,\d{3})+", na=False)
    last_is_comma = digits.str.rfind(",") > digits.str.rfind(".")

    normalised = np.select(
        [
            has_comma & has_dot & last_is_comma,    # "1.299,99" → European format
            has_comma & has_dot,                     # "1,299.99" → US format
            comma_is_thousands,                      # "1,299"    → thousands separator
            has_comma,                               # "349,00"   → decimal comma
        ],
        [
            digits.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
            digits.str.replace(",", "", regex=False),
            digits.str.replace(",", "", regex=False),
            digits.str.replace(",", ".", regex=False),
        ],
        default=digits,
    )
    price = pd.to_numeric(pd.Series(normalised, index=raw.index), errors="coerce")
    price = price.where(~missing)
    # A non-positive price is impossible for a sale → treat as missing, not as a value.
    price = price.where(price > 0)
    return price.astype("float64"), currency


def _count_changed(before: pd.Series, after: pd.Series) -> int:
    both = before.notna() & after.notna()
    return int((before[both].astype(str) != after[both].astype(str)).sum())


# ---------------------------------------------------------------------------
# Mission 1 / Bonus — profiling
# ---------------------------------------------------------------------------
def quality_report(df: pd.DataFrame) -> dict:
    """Dtypes, missing %, unique values, duplicates, numeric ranges, outliers."""
    report: dict = {
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isna().sum().to_dict(),
        "missing_pct": (df.isna().mean() * 100).round(1).to_dict(),
        "exact_duplicate_rows": int(df.duplicated().sum()),
    }
    if "id" in df:
        dup_ids = df.loc[df["id"].duplicated(keep=False), "id"]
        report["repeated_ids"] = sorted(dup_ids.unique().tolist())
    report["unique_values"] = {
        c: sorted(df[c].dropna().astype(str).unique().tolist())
        for c in ("region", "category", "channel") if c in df
    }
    num = df.select_dtypes(include="number")
    if not num.empty:
        report["numeric_ranges"] = num.agg(["min", "max", "mean"]).round(2).to_dict()
        q1, q3 = num.quantile(0.25), num.quantile(0.75)
        iqr = q3 - q1
        outliers = (num < q1 - 3 * iqr) | (num > q3 + 3 * iqr)
        report["iqr3_outliers"] = outliers.sum().astype(int).to_dict()
    return report


def profile_raw(raw: pd.DataFrame) -> None:
    print("=" * 70, "\nMISSION 1 — PROFILE THE DAMAGE\n" + "=" * 70)
    print(raw.head(), "\n")
    q = quality_report(raw)
    print("shape:", q["shape"])
    print("dtypes:", q["dtypes"])
    print("missing:", q["missing"])
    print("missing %:", q["missing_pct"])
    print("exact duplicate rows:", q["exact_duplicate_rows"])
    print("repeated ids:", q["repeated_ids"])
    for c, vals in q["unique_values"].items():
        print(f"unique {c}:", vals)
    # Issues that are not visible as NaN in the raw string data
    price = raw["price"].fillna("")
    print("non-standard price strings:",
          sorted(price[~price.str.fullmatch(r"\d+\.\d{2}")].unique().tolist()))
    print("non-integer quantities:",
          sorted(raw["quantity"].dropna()[~raw["quantity"].dropna().str.fullmatch(r"\d+")].unique().tolist()))
    bad_dates = pd.to_datetime(raw["order_date"], format="%d.%m.%Y", errors="coerce")
    print("unparseable dates:", raw.loc[bad_dates.isna(), "order_date"].tolist())
    print("dates after cutoff:", raw.loc[bad_dates > REPORT_CUTOFF, "order_date"].tolist())
    print()


# ---------------------------------------------------------------------------
# Mission 2 — cleaning
# ---------------------------------------------------------------------------
def clean_sales(df: pd.DataFrame, as_of: pd.Timestamp = REPORT_CUTOFF) -> tuple[pd.DataFrame, dict]:
    """Return a cleaned copy and a report of cleaning actions."""
    # Deep copy: the raw frame must stay untouched so the pipeline is auditable/re-runnable.
    raw = df.copy(deep=True)
    out = raw.copy(deep=True)
    report: dict = {"rows_in": len(raw), "fixed_values": {}, "set_to_missing": {}}

    # Keep the original CSV line number so every flagged row can be traced back.
    out.insert(0, "source_line", raw.index.to_numpy() + 2)

    # 1. Strip whitespace — " north ", " laptop pro 14 ", "Accessories " are the same values.
    for c in TEXT_COLS:
        out[c] = out[c].str.strip().str.replace(r"\s+", " ", regex=True)

    # 2. Standardise labels.
    # product: map to a canonical spelling (keeps "USB-C Hub"/"Webcam HD", which .title() breaks);
    # unknown products fall back to title case instead of being dropped.
    key = _norm_key(out["product"])
    out["product"] = key.map(PRODUCT_LOOKUP).fillna(out["product"].str.title())
    # region / category / channel: case is the only variation → title case.
    for c in ("region", "category", "channel"):
        out[c] = out[c].str.title()
    for c in ("product", "region", "category", "channel"):
        report["fixed_values"][c] = _count_changed(raw[c], out[c])

    # Category conflicts: the same product is filed under different categories
    # (e.g. Laptop Pro 14 as Accessories, Office Chair as Electronics). A product has one
    # category, so we take the product's majority category and flag the overridden rows.
    modal_cat = out.groupby("product")["category"].agg(lambda s: s.mode().iat[0])
    expected = out["product"].map(modal_cat)
    out["category_conflict"] = out["category"].ne(expected)
    out["original_category"] = out["category"].where(out["category_conflict"])
    out["category"] = expected
    report["fixed_values"]["category_reassigned"] = int(out["category_conflict"].sum())

    # 3. Price → float. Missing/'unknown'/invalid → NaN (never 0: a zero would silently
    #    drag totals down and hide the problem).
    out["price"], out["currency"] = _parse_price(out["price"])
    reformatted = raw["price"].notna() & out["price"].notna() & ~raw["price"].str.strip().str.fullmatch(r"\d+(\.\d+)?", na=False)
    report["fixed_values"]["price_reformatted"] = int(reformatted.sum())
    report["set_to_missing"]["price"] = int((raw["price"].notna() & out["price"].isna()).sum())
    out["foreign_currency"] = out["currency"].notna() & out["currency"].ne(BASE_CURRENCY)
    # Price outlier vs product median — catches e.g. a USB-C Hub at 1299.99 or a mouse at 331.55.
    median = out.groupby("product")["price"].transform("median")
    ratio = out["price"] / median
    lo, hi = PRICE_OUTLIER_RATIO
    out["price_outlier"] = ((ratio < lo) | (ratio > hi)).fillna(False).astype(bool)

    # 4. Quantity → Int64.
    #    blank          → <NA>  (unknown, not zero)
    #    non-numeric    → <NA> + flag  ("five" is probably 5, but guessing is not our call)
    #    zero/negative  → <NA> + flag  (a sale of 0 or -3 items is impossible; -3 might be a
    #                                    return, but there is no returns field, so it must not
    #                                    reduce sales silently)
    #    non-integer    → <NA> + flag
    qraw = out["quantity"]
    qnum = pd.to_numeric(qraw, errors="coerce")
    out["qty_missing"] = qraw.isna() | qraw.eq("")
    out["qty_non_numeric"] = ~out["qty_missing"] & qnum.isna()
    out["qty_non_positive"] = qnum.le(0).fillna(False).astype(bool)
    non_integer = qnum.notna() & qnum.ne(qnum.round())
    valid_q = qnum.gt(0) & ~non_integer
    out["quantity"] = qnum.where(valid_q).astype("Int64")
    out["qty_suspicious_large"] = out["quantity"].ge(SUSPICIOUS_QTY).fillna(False).astype(bool)
    report["set_to_missing"]["quantity"] = int((qraw.notna() & qraw.ne("") & out["quantity"].isna()).sum())

    # 5. Dates: fixed DD.MM.YYYY format (no dayfirst guessing). Impossible dates such as
    #    31.02.2026 → NaT + flag. Dates after the reporting period are kept but flagged.
    out["order_date"] = pd.to_datetime(out["order_date"], format="%d.%m.%Y", errors="coerce")
    out["invalid_date"] = out["order_date"].isna()
    out["future_date"] = out["order_date"].gt(as_of).fillna(False).astype(bool)
    report["set_to_missing"]["order_date"] = int(out["invalid_date"].sum())

    # 6a. Exact duplicates (after normalisation, so whitespace/case variants are caught too):
    #     a double export of the same order — dropping it is lossless.
    dup_mask = out.drop(columns="source_line").duplicated(keep="first")
    report["exact_duplicates_dropped"] = int(dup_mask.sum())
    out = out.loc[~dup_mask]

    # 6b. Same id, different content: the records differ only in order_date, which looks like
    #     a re-export of an updated order. We keep the NEWEST record (latest valid date) and
    #     set id_conflict=True so a human can confirm. Dropped versions are listed in the report.
    out["id_conflict"] = out["id"].duplicated(keep=False)
    order = out.sort_values(["id", "order_date", "source_line"], na_position="first")
    keep_mask = ~order["id"].duplicated(keep="last")
    dropped = order.loc[~keep_mask]
    report["id_conflicts_dropped"] = int(len(dropped))
    report["id_conflict_dropped_lines"] = dict(zip(dropped["id"], dropped["source_line"].astype(int)))
    out = order.loc[keep_mask].sort_values("source_line").reset_index(drop=True)

    report["rows_out"] = len(out)
    report["rows_dropped"] = report["rows_in"] - report["rows_out"]
    report["remaining_missing"] = {
        c: int(v) for c, v in out[["order_date", "quantity", "price"]].isna().sum().items()
    }
    report["flags"] = {
        c: int(out[c].sum())
        for c in ("category_conflict", "foreign_currency", "price_outlier", "qty_missing",
                  "qty_non_numeric", "qty_non_positive", "qty_suspicious_large",
                  "invalid_date", "future_date", "id_conflict")
    }
    return out, report


# ---------------------------------------------------------------------------
# Mission 3 — derived columns
# ---------------------------------------------------------------------------
def product_label_vectorised(df: pd.DataFrame) -> pd.Series:
    qty = df["quantity"].astype("string").fillna("?")
    return df["product"] + " x" + qty


def product_label_apply(df: pd.DataFrame) -> pd.Series:
    return df.apply(
        lambda r: f"{r['product']} x{'?' if pd.isna(r['quantity']) else int(r['quantity'])}",
        axis=1,
    )


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy enriched with derived columns."""
    out = df.copy(deep=True)
    qty = out["quantity"].to_numpy(dtype="float64", na_value=np.nan)

    # NaN propagates: an order with unknown price or quantity has an unknown total, not 0.
    out["total"] = (qty * out["price"]).round(2)
    out["total_with_vat"] = (out["total"] * (1 + VAT_RATE)).round(2)
    # Nullable boolean: <NA> when quantity is unknown, so "not bulk" ≠ "don't know".
    out["is_bulk"] = out["quantity"].ge(BULK_QTY)
    out["priority"] = np.select(
        [out["total"].isna(), out["total"] >= 5000, out["total"] >= 1000],
        ["unknown", "high", "medium"],
        default="low",
    )
    out["region_code"] = out["region"].map(REGION_CODES).fillna(UNKNOWN_REGION_CODE)
    out["product_label"] = product_label_vectorised(out)

    # Manual-review flag: one human-readable reason string per row, built column-wise.
    reasons = {
        "invalid_date": out["invalid_date"],
        "future_date": out["future_date"],
        "missing_price": out["price"].isna(),
        "missing_qty": out["qty_missing"],
        "non_numeric_qty": out["qty_non_numeric"],
        "non_positive_qty": out["qty_non_positive"],
        "large_qty": out["qty_suspicious_large"],
        "price_outlier": out["price_outlier"],
        "foreign_currency": out["foreign_currency"],
        "category_conflict": out["category_conflict"],
        "id_conflict": out["id_conflict"],
    }
    reason = pd.Series("", index=out.index, dtype="object")
    for name, mask in reasons.items():
        reason = reason + np.where(mask.to_numpy(dtype=bool), name + ";", "")
    out["review_reason"] = reason.str.rstrip(";")
    out["needs_review"] = out["review_reason"].ne("")
    return out


# ---------------------------------------------------------------------------
# Mission 5 — pipeline
# ---------------------------------------------------------------------------
def prepare_sales(df: pd.DataFrame, as_of: pd.Timestamp = REPORT_CUTOFF) -> tuple[pd.DataFrame, dict]:
    """Run the full repeatable pipeline. Pure function: input is never modified."""
    cleaned, report = clean_sales(df, as_of=as_of)
    enriched = add_features(cleaned)
    report["needs_review"] = int(enriched["needs_review"].sum())
    report["total_sales_known"] = round(float(enriched["total"].sum()), 2)
    return enriched, report


# ---------------------------------------------------------------------------
# Mission 4 — management questions
# ---------------------------------------------------------------------------
def management_answers(df: pd.DataFrame) -> dict:
    a: dict = {}
    # pandas sum() skips NaN: totals cover only orders with a usable price AND quantity.
    a["sales_by_category"] = df.groupby("category")["total"].sum().round(2).sort_values(ascending=False)
    a["top5_orders"] = df.nlargest(5, "total")[["id", "product", "quantity", "price", "currency", "total", "review_reason"]]
    a["orders_by_region"] = df["region"].value_counts()
    unusable = df["price"].isna() | df["quantity"].isna()
    a["missing_price_or_qty"] = {
        "any": int(unusable.sum()),
        "price": int(df["price"].isna().sum()),
        "quantity": int(df["quantity"].isna().sum()),
    }
    trusted = ~df["needs_review"]
    a["total_sales"] = {
        "all_computable_orders": round(float(df["total"].sum()), 2),
        "computable_orders": int(df["total"].notna().sum()),
        "excluding_review_rows": round(float(df.loc[trusted, "total"].sum()), 2),
        "clean_orders": int(trusted.sum()),
        "with_vat_all_computable": round(float(df["total_with_vat"].sum()), 2),
        # Mixing USD/EUR into a PLN sum is wrong, and outlier prices are likely entry errors:
        "pln_excl_price_outliers": round(float(
            df.loc[~df["foreign_currency"] & ~df["price_outlier"], "total"].sum()), 2),
    }
    a["review"] = df.loc[df["needs_review"], ["source_line", "id", "order_date", "product", "quantity", "price", "review_reason"]]
    a["region_x_category"] = df.pivot_table(
        index="region", columns="category", values="total", aggfunc="sum", margins=True
    ).round(2)
    a["region_x_category_orders"] = pd.crosstab(df["region"], df["category"], margins=True)
    return a


def benchmark(n: int = 100_000) -> dict:
    rng = np.random.default_rng(0)
    big = pd.DataFrame({
        "product": rng.choice(CANONICAL_PRODUCTS, n),
        "quantity": pd.array(rng.integers(1, 30, n), dtype="Int64"),
    })
    t0 = time.perf_counter(); v = product_label_vectorised(big); t1 = time.perf_counter()
    a = product_label_apply(big); t2 = time.perf_counter()
    assert (v.astype(str) == a.astype(str)).all()
    return {"rows": n, "vectorised_s": round(t1 - t0, 4), "apply_s": round(t2 - t1, 4),
            "speedup": round((t2 - t1) / (t1 - t0), 1)}


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pd.set_option("display.width", 200, "display.max_columns", 30, "display.max_rows", 100)
    raw = pd.read_csv("dirty_sales.csv", dtype=str)
    raw_snapshot = raw.copy(deep=True)

    profile_raw(raw)

    print("=" * 70, "\nMISSION 2+3+5 — PIPELINE\n" + "=" * 70)
    cleaned, report = prepare_sales(raw)
    assert raw.equals(raw_snapshot), "raw DataFrame was modified!"
    for k, v in report.items():
        print(f"{k}: {v}")
    print(cleaned[["id", "order_date", "product", "category", "region", "quantity", "price",
                   "total", "priority", "region_code", "product_label"]].head(), "\n")

    print("=" * 70, "\nMISSION 4 — MANAGEMENT QUESTIONS\n" + "=" * 70)
    ans = management_answers(cleaned)
    for k, v in ans.items():
        print(f"\n--- {k} ---\n{v}")

    print("\n--- post-clean quality report ---")
    q = quality_report(cleaned[["quantity", "price", "total"]])
    print(q["numeric_ranges"], q["iqr3_outliers"])

    if "--bench" in sys.argv:
        print("\n--- benchmark ---\n", benchmark())
    cleaned.to_csv("clean_sales.csv", index=False)
    print("\nwrote clean_sales.csv")
