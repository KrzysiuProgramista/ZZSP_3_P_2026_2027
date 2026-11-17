"""Data Rescue: repeatable cleaning pipeline for dirty_sales.csv.

Completed version of starter-2.py.  Public API:

    clean_sales(df)    -> (cleaned_df, report)   Mission 2
    add_features(df)   -> enriched copy          Mission 3
    flag_for_review(df)-> copy + review columns  Mission 4
    prepare_sales(df)  -> (final_df, report)     Mission 5
    quality_report(df) -> dict                   Bonus

Design rules followed everywhere:
  * the input DataFrame is never modified (every function works on a copy);
  * no row loops, no inplace=True; vectorised .str / np.select / .map only;
  * a missing or invalid value becomes NaN / <NA>, never 0;
  * every decision is explained in a comment next to the code that makes it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Business rules / assumptions (kept in one place so they are easy to change)
# --------------------------------------------------------------------------
# The export is dated in early November 2026; anything later than this cannot
# be a real, already-placed order.  A fixed constant (not "today") keeps the
# pipeline deterministic: the same input always gives the same output.
EXPORT_DATE = pd.Timestamp("2026-11-03")

VAT_RATE = 0.23              # Polish VAT, as specified in the brief
BULK_THRESHOLD = 10          # is_bulk: quantity >= 10
HIGH_TOTAL = 5000            # priority = high   when total >= 5000
MEDIUM_TOTAL = 1000          # priority = medium when total >= 1000
SUSPICIOUS_QTY = 20          # quantity > 20 is unusually large -> human check
PRICE_OUTLIER_RATIO = 2.0    # price > 2x or < 0.5x the product's median price

TEXT_COLS = ["id", "product", "category", "region", "channel"]
BUSINESS_COLS = ["id", "order_date", "product", "category", "region",
                 "quantity", "price", "channel"]

# Tokens that mean "no price / no value" even though they are not empty.
PLACEHOLDERS = {"unknown", "n/a", "na", "none", "null", "nan", "-", "?", "tbd"}

# Product catalogue: canonical spelling + the category that product belongs to.
# Why a catalogue: the category column contradicts the product in several rows
# (e.g. a laptop filed under Accessories).  The product name is the more
# specific field, so it is treated as the source of truth for the category and
# disagreements are flagged instead of being silently accepted.
PRODUCT_CATALOGUE = {
    "laptop pro 14": ("Laptop Pro 14", "Electronics"),
    "monitor 27": ("Monitor 27", "Electronics"),
    "webcam hd": ("Webcam HD", "Electronics"),
    "headphones": ("Headphones", "Electronics"),
    "wireless mouse": ("Wireless Mouse", "Accessories"),
    "mechanical keyboard": ("Mechanical Keyboard", "Accessories"),
    "usb-c hub": ("USB-C Hub", "Accessories"),
    "office chair": ("Office Chair", "Furniture"),
    "standing desk": ("Standing Desk", "Furniture"),
    "desk lamp": ("Desk Lamp", "Furniture"),
    "notebook pack": ("Notebook Pack", "Stationery"),
    "whiteboard": ("Whiteboard", "Stationery"),
}
PRODUCT_NAME = {k: v[0] for k, v in PRODUCT_CATALOGUE.items()}
PRODUCT_CATEGORY = {k: v[1] for k, v in PRODUCT_CATALOGUE.items()}

REGION_CODES = {"North": "N", "South": "S", "East": "E", "West": "W"}

# A quantity written as a word ("five") is unambiguous, so we convert it
# instead of throwing the order away.  It is still reported as a fixed value.
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "twenty": 20,
}

_CURRENCY_RE = r"(?i)[$€£]|zł|pln|usd|eur"


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def _as_bool(mask: pd.Series) -> pd.Series:
    """Nullable boolean result of a .str test -> plain bool (NA counts as False)."""
    return mask.fillna(False).astype(bool)


def _blank_to_na(s: pd.Series) -> pd.Series:
    """Trim + collapse inner whitespace; empty string becomes <NA>.

    Blank cells are 'missing', not a value, so they must be NA and never ''.
    """
    s = s.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    return s.mask(_as_bool(s.eq("")))


# --------------------------------------------------------------------------
# Column parsers (each returns the parsed values AND a note explaining the
# outcome, so the report and the manual-review list can be built later).
# --------------------------------------------------------------------------
def _parse_price(raw: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (price float64, note string, was_reformatted bool).

    Handles: $ / € / £ / zł symbols, thousands separators ("1,299.99",
    "1.299,99"), decimal commas ("349,00"), blanks and 'unknown'.
    Anything that cannot be read with confidence becomes NaN -- never 0,
    because 0 would silently turn "we do not know" into "it was free".
    """
    s = _blank_to_na(raw)
    is_token = s.str.lower().isin(PLACEHOLDERS)
    has_symbol = _as_bool(s.str.contains(_CURRENCY_RE, regex=True))

    # Remove currency markers and any whitespace (incl. non-breaking spaces).
    core = (s.str.replace(_CURRENCY_RE, "", regex=True)
              .str.replace(r"\s", "", regex=True))

    # Three recognised number layouts.  Ambiguous things like "1.2.3" match
    # none of them and therefore become NaN instead of a guess.
    us_style = _as_bool(core.str.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?"))
    eu_style = _as_bool(core.str.fullmatch(
        r"-?\d{1,3}(?:\.\d{3})*,\d+|-?\d+,\d+"))
    plain = _as_bool(core.str.fullmatch(r"-?\d+(?:\.\d+)?"))

    norm = pd.Series(pd.NA, index=s.index, dtype="string")
    # Order matters: "1,299" fits both eu_style and us_style; we read it as
    # thousands (1299) because prices here always carry 2 decimals.
    norm = norm.mask(eu_style, core.str.replace(".", "", regex=False)
                                   .str.replace(",", ".", regex=False))
    norm = norm.mask(us_style, core.str.replace(",", "", regex=False))
    norm = norm.mask(plain, core)
    value = pd.to_numeric(norm, errors="coerce").astype("float64")

    # A price of 0 or below is not a real selling price -> treat as invalid.
    non_positive = value <= 0
    value = value.mask(non_positive)

    unparseable = s.notna() & ~is_token & norm.isna()
    note = np.select(
        [s.isna(), is_token, non_positive, unparseable,
         has_symbol & value.notna()],
        ["blank", "unknown", "non_positive", "unparseable", "currency_symbol"],
        default="",
    )
    reformatted = value.notna() & (us_style | eu_style | has_symbol)
    return value, pd.Series(note, index=s.index, dtype="string"), reformatted


def _parse_quantity(raw: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return (quantity Int64, note string).

    * blank / text we cannot read -> <NA>
    * "five"                      -> 5 (unambiguous, reported as converted)
    * 0 or negative               -> <NA>: an order for zero or -3 items is not
      a valid sale.  It might be a return or a typo; we cannot know which, so
      we do NOT invent a number, we keep the row (so order counts stay honest)
      and flag it for human review.
    """
    s = _blank_to_na(raw)
    is_int = _as_bool(s.str.fullmatch(r"-?\d+(?:\.0+)?"))
    digits = pd.to_numeric(s.where(is_int), errors="coerce").astype("float64")
    words = pd.to_numeric(s.str.lower().map(NUMBER_WORDS),
                          errors="coerce").astype("float64")
    value = digits.where(digits.notna(), words)
    from_word = digits.isna() & words.notna()

    non_positive = value <= 0
    value = value.mask(non_positive)
    non_numeric = s.notna() & value.isna() & ~non_positive

    note = np.select(
        [s.isna(), non_positive, non_numeric, from_word],
        ["blank", "non_positive", "non_numeric", "converted_from_word"],
        default="",
    )
    return (value.astype("Int64"),
            pd.Series(note, index=s.index, dtype="string"))


def _parse_date(raw: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return (order_date datetime64, note string).

    Main format is DD.MM.YYYY.  Impossible dates such as 31.02.2026 become
    NaT (we must not guess which day was meant).  Dates after EXPORT_DATE are
    kept but noted, because the order may still exist with a typo in the year.
    """
    s = _blank_to_na(raw)
    parsed = pd.to_datetime(s, format="%d.%m.%Y", errors="coerce")
    # Cheap fallback so a stray ISO date is not thrown away.
    iso = pd.to_datetime(s.where(parsed.isna()), format="%Y-%m-%d",
                         errors="coerce")
    parsed = parsed.fillna(iso)
    note = np.select(
        [s.isna(), parsed.isna(), parsed > EXPORT_DATE],
        ["blank", "invalid", "future"],
        default="",
    )
    return parsed, pd.Series(note, index=s.index, dtype="string")


# --------------------------------------------------------------------------
# Mission 2: cleaning
# --------------------------------------------------------------------------
def clean_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return a cleaned copy and a report of cleaning actions.

    The input is never modified.  Counts in the 'fixed' section describe the
    input rows (before duplicates are removed).
    """
    out = df.copy(deep=True)                      # raw stays untouched
    rows_in = len(out)
    fixed: dict[str, int] = {}

    # Keep a pointer back to the CSV line (header = line 1) so every cleaned
    # row can be traced to the raw file by a human reviewer.
    out.insert(0, "csv_line", np.arange(rows_in) + 2)

    # ---- 1. strings: strip whitespace, blanks -> NA -----------------------
    raw_text = {c: out[c].astype("string") for c in TEXT_COLS}
    for col in TEXT_COLS:
        trimmed = raw_text[col].str.strip().str.replace(r"\s+", " ", regex=True)
        # count cells whose text changed only because of whitespace
        fixed[f"{col}_whitespace_trimmed"] = int(
            _as_bool(raw_text[col].ne(trimmed)).sum())
        out[col] = _blank_to_na(out[col])

    out["id"] = out["id"].str.upper()             # ids are case-insensitive keys

    # ---- 2. standardise product / category / region / channel -------------
    # Case + spacing variants ("WIRELESS MOUSE", " laptop pro 14 ") are the
    # same thing, so they are mapped onto one canonical spelling.
    product_key = out["product"].str.lower()
    product_clean = product_key.map(PRODUCT_NAME).astype("string")
    unknown_product = product_clean.isna() & out["product"].notna()
    product_clean = product_clean.fillna(out["product"])   # keep unseen products as-is
    fixed["product_standardised"] = int(
        _as_bool(product_clean.ne(raw_text["product"])).sum())
    out["product"] = product_clean

    category_clean = out["category"].str.title()
    catalogue_cat = product_key.map(PRODUCT_CATEGORY).astype("string")
    # Category disagreeing with the product's catalogue category = conflict.
    # We keep the catalogue category (product is more specific) and flag it.
    out["category_conflict"] = _as_bool(
        catalogue_cat.notna() & category_clean.notna()
        & catalogue_cat.ne(category_clean))
    fixed["category_standardised_case"] = int(
        _as_bool(category_clean.ne(raw_text["category"])
                 & ~category_clean.isna()).sum())
    fixed["category_overridden_by_product"] = int(out["category_conflict"].sum())
    fixed["category_filled_from_product"] = int(
        (category_clean.isna() & catalogue_cat.notna()).sum())
    out["category"] = catalogue_cat.fillna(category_clean)

    # Region / channel are small closed sets: Title Case is enough.  Values
    # outside the known set are kept (not deleted) and show up as 'UNK' later.
    for col in ("region", "channel"):
        cleaned = out[col].str.title()
        fixed[f"{col}_standardised"] = int(
            _as_bool(cleaned.ne(raw_text[col])).sum())
        out[col] = cleaned

    # ---- 3. numeric / date columns ----------------------------------------
    out["price"], out["price_note"], reformatted = _parse_price(out["price"])
    out["quantity"], out["quantity_note"] = _parse_quantity(out["quantity"])
    out["order_date"], out["date_note"] = _parse_date(out["order_date"])
    fixed["price_format_normalised"] = int(reformatted.sum())
    fixed["quantity_converted_from_word"] = int(
        (out["quantity_note"] == "converted_from_word").sum())

    # Notes that mean "value was thrown away (now NaN/NaT)" vs "value kept but
    # worth a second look".  Kept separate so the report is not misleading.
    set_missing = {"price": ["blank", "unknown", "unparseable", "non_positive"],
                   "quantity": ["blank", "non_positive", "non_numeric"],
                   "order_date": ["blank", "invalid"]}
    notes = {"price": out["price_note"], "quantity": out["quantity_note"],
             "order_date": out["date_note"]}
    invalid = {c: {k: int((notes[c] == k).sum()) for k in keys
                   if (notes[c] == k).any()}
               for c, keys in set_missing.items()}
    kept_but_noted = {
        "price_had_currency_symbol": int((out["price_note"] == "currency_symbol").sum()),
        "future_dates": int((out["date_note"] == "future").sum()),
    }

    # ---- 4. duplicates ----------------------------------------------------
    # (a) Exact duplicates: every business column identical -> pure noise
    #     (a re-exported line).  Drop all but the first.
    exact_dup = out.duplicated(subset=BUSINESS_COLS, keep="first")
    out = out.loc[~exact_dup]

    # (b) Same id, different content: two versions of one order.  DECISION:
    #     keep the newest (latest order_date; if tied, the later CSV line) and
    #     flag it.  We do not average or merge, and we keep the flag so that a
    #     human can still confirm which version is right.
    out["id_conflict"] = out["id"].notna() & out["id"].duplicated(keep=False)
    newest_last = out.sort_values("order_date", kind="mergesort",
                                  na_position="first")
    stale = newest_last["id"].notna() & newest_last["id"].duplicated(keep="last")
    dropped_stale = int(stale.sum())
    out = newest_last.loc[~stale].sort_index().reset_index(drop=True)

    report = {
        "rows_in": rows_in,
        "rows_out": len(out),
        "dropped_exact_duplicates": int(exact_dup.sum()),
        "dropped_older_duplicate_ids": dropped_stale,
        "ids_with_conflict_kept_newest": int(out["id_conflict"].sum()),
        "fixed_values": fixed,
        "invalid_values_set_to_missing": invalid,
        "kept_but_noted": kept_but_noted,
        "unrecognised_products": int(unknown_product.sum()),
        "remaining_missing": {c: int(out[c].isna().sum())
                              for c in BUSINESS_COLS},
    }
    return out, report


# --------------------------------------------------------------------------
# Mission 3: derived columns
# --------------------------------------------------------------------------
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy enriched with derived columns (all vectorised)."""
    out = df.copy(deep=True)

    # Int64 -> float64 so that <NA> becomes NaN and the arithmetic propagates
    # "unknown" instead of inventing a number.
    qty = out["quantity"].astype("float64")
    out["total"] = qty * out["price"]                     # NaN if either is missing
    out["total_with_vat"] = (out["total"] * (1 + VAT_RATE)).round(2)

    # Unknown quantity cannot be shown to be >= 10, so it is False; the
    # missing quantity itself stays visible in the quantity column.
    out["is_bulk"] = (qty >= BULK_THRESHOLD).fillna(False).astype(bool)

    # Missing totals get their own label ("unknown") instead of silently
    # falling into "low" -- NaN >= 1000 is False, so order of conditions matters.
    out["priority"] = np.select(
        [out["total"].isna(), out["total"] >= HIGH_TOTAL,
         out["total"] >= MEDIUM_TOTAL],
        ["unknown", "high", "medium"],
        default="low",
    )

    # Unknown / missing region -> "UNK" rather than NaN so group-bys keep them.
    out["region_code"] = out["region"].map(REGION_CODES).fillna("UNK")

    # Vectorised string concatenation (fast).  Unknown quantity shows as "x?".
    out["product_label"] = (out["product"] + " x"
                            + out["quantity"].astype("string").fillna("?"))
    return out


def product_label_apply(df: pd.DataFrame) -> pd.Series:
    """Same label via apply(axis=1) -- only here to compare against the
    vectorised version (see the benchmark in analysis.py)."""
    def label(row):
        q = "?" if pd.isna(row["quantity"]) else str(row["quantity"])
        return f"{row['product']} x{q}"
    return df.apply(label, axis=1)


# --------------------------------------------------------------------------
# Mission 4 helper: manual-review flags
# --------------------------------------------------------------------------
def flag_for_review(df: pd.DataFrame) -> pd.DataFrame:
    """Add price_outlier, review_reason and needs_review columns."""
    out = df.copy(deep=True)

    # A price far from the product's usual price is suspicious even if it
    # parsed fine (e.g. a USB-C Hub at 1299.99 when it normally costs ~130).
    # Median is used because it is not dragged around by the outliers.
    median_price = out.groupby("product")["price"].transform("median")
    ratio = out["price"] / median_price
    out["price_outlier"] = ((ratio > PRICE_OUTLIER_RATIO)
                            | (ratio < 1 / PRICE_OUTLIER_RATIO)).fillna(False)

    checks = {
        "invalid_date": out["date_note"].isin(["invalid", "blank"]),
        "future_date": out["date_note"].eq("future"),
        "missing_price": out["price"].isna(),
        "price_currency_symbol": out["price_note"].eq("currency_symbol"),
        "price_outlier": out["price_outlier"],
        "missing_quantity": out["quantity"].isna(),
        "quantity_non_positive": out["quantity_note"].eq("non_positive"),
        "quantity_was_text": out["quantity_note"].eq("converted_from_word"),
        "suspicious_quantity": out["quantity"].gt(SUSPICIOUS_QTY).fillna(False),
        "conflicting_id": out["id_conflict"],
        "category_mismatch": out["category_conflict"],
    }
    reason = pd.Series("", index=out.index, dtype="object")
    for name, mask in checks.items():          # loop over RULES, not rows
        reason = reason + np.where(mask.astype(bool), name + "; ", "")
    out["review_reason"] = reason.str.rstrip("; ")
    out["needs_review"] = out["review_reason"].ne("")
    return out


# --------------------------------------------------------------------------
# Mission 5: repeatable pipeline
# --------------------------------------------------------------------------
def prepare_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Run the full repeatable pipeline.

    Pure function: does not touch `df`, uses no global state, and gives an
    identical result when called twice on the same input.
    """
    cleaned, report = clean_sales(df)
    enriched = flag_for_review(add_features(cleaned))
    report["rows_needing_review"] = int(enriched["needs_review"].sum())
    report["rows_without_usable_total"] = int(enriched["total"].isna().sum())
    return enriched, report


# --------------------------------------------------------------------------
# Bonus: generic data-quality report
# --------------------------------------------------------------------------
def quality_report(df: pd.DataFrame, max_unique: int = 20) -> dict:
    """dtypes, missing %, unique values, duplicates, numeric ranges, outliers."""
    rep: dict = {"shape": df.shape,
                 "dtypes": df.dtypes.astype(str).to_dict()}
    rep["missing_pct"] = (df.isna().mean() * 100).round(1).to_dict()
    rep["exact_duplicate_rows"] = int(df.duplicated().sum())
    if "id" in df:
        rep["repeated_id_rows"] = int(df["id"].duplicated(keep=False).sum())

    # Low-cardinality text columns: show every distinct value.
    rep["unique_values"] = {
        c: sorted(df[c].dropna().astype(str).unique().tolist())
        for c in df.columns
        if df[c].nunique(dropna=True) <= max_unique
        and not pd.api.types.is_numeric_dtype(df[c])
        and not pd.api.types.is_bool_dtype(df[c])
        and not pd.api.types.is_datetime64_any_dtype(df[c])
    }

    # Numeric ranges + Tukey IQR outliers (value < Q1-1.5*IQR or > Q3+1.5*IQR).
    ranges, outliers = {}, {}
    for c in df.select_dtypes("number").columns:
        s = df[c].astype("float64").dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile([0.25, 0.75])
        fence = 1.5 * (q3 - q1)
        ranges[c] = {"min": float(s.min()), "median": float(s.median()),
                     "max": float(s.max())}
        outliers[c] = int(((s < q1 - fence) | (s > q3 + fence)).sum())
    rep["numeric_ranges"] = ranges
    rep["iqr_outlier_counts"] = outliers
    return rep


if __name__ == "__main__":
    raw = pd.read_csv("dirty_sales.csv", dtype=str)
    cleaned, report = prepare_sales(raw)
    print(report)
    print(cleaned.head())
