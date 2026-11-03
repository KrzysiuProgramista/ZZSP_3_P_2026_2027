"""Data Rescue: analysis, management answers and verdict.

Run:  python analysis.py        (needs dirty_sales.csv next to this file)
Also writes: clean_sales_cleaned.csv and manual_review.csv
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from sales_pipeline import (EXPORT_DATE, SUSPICIOUS_QTY, add_features,
                            prepare_sales, product_label_apply,
                            quality_report)

HERE = Path(__file__).parent
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def section(title: str) -> None:
    print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78)


# ==========================================================================
# MISSION 1: profile the damage (on the RAW data, which is never modified)
# ==========================================================================
section("MISSION 1 - PROFILE THE DAMAGE")
# dtype=str: read everything as text so pandas cannot hide problems by
# guessing types (e.g. "$1,299.99" would otherwise force the column to object).
raw = pd.read_csv(HERE / "dirty_sales.csv", dtype=str)
raw_snapshot = raw.copy(deep=True)       # used at the end to prove raw is intact

print("shape:", raw.shape)
print(raw.head(), "\n")
print("dtypes (all text on purpose):\n", raw.dtypes, "\n")

missing = pd.DataFrame({"missing": raw.isna().sum(),
                        "missing_%": (raw.isna().mean() * 100).round(1)})
print("Missing values (NaN/blank):\n", missing, "\n")

# Placeholder text that LOOKS like data but means 'missing' is invisible to isna().
placeholder = raw["price"].str.strip().str.lower().eq("unknown").sum()
print(f"Hidden missing: {placeholder} prices are the text 'unknown'\n")

dup_rows = raw[raw.duplicated(keep=False)]
dup_ids = raw[raw["id"].duplicated(keep=False)].sort_values("id")
print(f"Exact duplicate rows (all copies): {len(dup_rows)} "
      f"({raw.duplicated().sum()} redundant)")
print(f"Rows sharing a repeated id: {len(dup_ids)}")
print(dup_ids.to_string(), "\n")

for col in ["region", "category", "channel"]:
    # repr() makes leading/trailing spaces visible
    print(f"unique {col}: {[repr(v) for v in sorted(raw[col].dropna().unique())]}")

# --- data-quality issues found (counts computed, not typed by hand) -------
cleaned, report = prepare_sales(raw)          # needed for a few of the counts
plain_price = raw["price"].str.fullmatch(r"\d+(\.\d+)?").fillna(False)
date_parsed = pd.to_datetime(raw["order_date"].str.strip(),
                             format="%d.%m.%Y", errors="coerce")
print("\nDATA-QUALITY ISSUES FOUND")
issues = [
    ("Inconsistent text (case / spaces)",
     f"region has {raw['region'].nunique()} spellings for 4 regions; product "
     f"and category also vary in case/whitespace"),
    ("Mixed price formats / placeholders",
     f"{(~plain_price & raw['price'].notna()).sum()} non-numeric price strings "
     f"($1,299.99, '€ 349,00', 'unknown')"),
    ("Missing values",
     f"price: {raw['price'].isna().sum()} blank + {placeholder} 'unknown'; "
     f"quantity: {raw['quantity'].isna().sum()} blank"),
    ("Impossible / unreadable quantities",
     "0, -3 and the word 'five' in the quantity column"),
    ("Invalid and out-of-range dates",
     f"{date_parsed.isna().sum()} impossible dates (31.02.2026) and "
     f"{(date_parsed > EXPORT_DATE).sum()} date in the future (05.12.2027)"),
    ("Duplicates",
     f"{raw.duplicated().sum()} exact duplicate row and an id (ORD-0040) "
     f"repeated with a different date"),
    ("Category contradicts product",
     f"{report['fixed_values']['category_overridden_by_product']} rows, e.g. a "
     f"laptop filed as Accessories"),
    ("Suspicious prices",
     f"{int(cleaned['price_outlier'].sum())} prices far from the product's "
     f"normal price (USB-C Hub at 1299.99 / 349, Wireless Mouse at 331.55)"),
]
for i, (name, detail) in enumerate(issues, 1):
    print(f" {i}. {name}: {detail}")

all_ids = set(raw["id"].str.extract(r"(\d+)")[0].astype(int))
gap = sorted(set(range(1, max(all_ids) + 1)) - all_ids)
print(f" 9. Gap in id sequence: ORD-{gap[0]:04d} .. ORD-{gap[-1]:04d} never "
      f"appear (possible lost orders)" if gap else "")

# ==========================================================================
# MISSION 2: clean (clean_sales lives in sales_pipeline.py)
# ==========================================================================
section("MISSION 2 - CLEANING REPORT")
import json
print(json.dumps(report, indent=2))

# ==========================================================================
# MISSION 3: derived columns
# ==========================================================================
section("MISSION 3 - DERIVED COLUMNS")
cols = ["id", "product", "quantity", "price", "total", "total_with_vat",
        "is_bulk", "priority", "region_code", "product_label"]
print(cleaned[cols].head(8).to_string(), "\n")
print("priority counts:\n", cleaned["priority"].value_counts().to_string(), "\n")
print("region_code counts:\n", cleaned["region_code"].value_counts().to_string())

# Vectorised concat vs apply(axis=1): same answer?
via_apply = product_label_apply(cleaned)
same = bool((via_apply.astype("string") == cleaned["product_label"]).all())
print(f"\nvectorised label == apply(axis=1) label: {same}")

# ==========================================================================
# MISSION 4: management questions
# ==========================================================================
section("MISSION 4 - MANAGEMENT QUESTIONS")
df = cleaned

print("Q1. Which category has the highest total sales value?")
by_cat = df.groupby("category")["total"].sum().sort_values(ascending=False)
print(by_cat.round(2).to_string())
print(f"-> {by_cat.index[0]} leads with {by_cat.iloc[0]:,.2f} "
      f"({by_cat.iloc[0] / by_cat.sum():.0%} of the known total). Category is "
      f"taken from the product (see cleaning notes). Orders with no usable "
      f"price/quantity are excluded, so every category is understated by those orders.\n")

print("Q2. Five orders with the highest total value")
top5 = df.nlargest(5, "total")[["id", "product", "quantity", "price", "total",
                                "needs_review", "review_reason"]]
print(top5.to_string(index=False))
top1 = top5.iloc[0]
print(f"-> Only {int(top5['needs_review'].sum())} of these 5 is on the review "
      f"list: the others have normal prices and plausible bulk quantities, so "
      f"they are not data errors. But {top1['id']} alone is "
      f"{top1['total'] / df['total'].sum():.0%} of all known sales, and the top "
      f"5 together are {top5['total'].sum() / df['total'].sum():.0%}: results "
      f"are highly concentrated, so confirming these orders matters most.\n")

print("Q3. Which region has the most orders?")
by_region = df["region"].value_counts()
print(by_region.to_string())
leaders = by_region[by_region == by_region.max()].index.tolist()
print(f"-> {' and '.join(leaders)} {'are tied' if len(leaders) > 1 else 'leads'} "
      f"with {by_region.max()} orders each. Counts include orders with a "
      f"missing price, because they are real orders.\n")

print("Q4. Orders missing a usable price or quantity")
no_price, no_qty = df["price"].isna(), df["quantity"].isna()
print(f"missing price: {no_price.sum()}, missing quantity: {no_qty.sum()}, "
      f"either: {(no_price | no_qty).sum()} of {len(df)} orders "
      f"({(no_price | no_qty).mean():.1%})\n")

print("Q5. Total sales value after cleaning")
total = df["total"].sum()                 # .sum() skips NaN by design
clean_only = df.loc[~df["needs_review"], "total"].sum()
print(f"total = {total:,.2f}  (incl. VAT {df['total_with_vat'].sum():,.2f})")
print(f"Missing handling: {int(df['total'].isna().sum())} orders have no "
      f"usable total and contribute NOTHING (they are not valued at 0 and not "
      f"estimated), so this is a lower bound.")
print(f"Sensitivity: only orders with no review flag add up to "
      f"{clean_only:,.2f} ({clean_only / total:.0%} of the total). "
      f"{total - clean_only:,.2f} depends on data a human should confirm.\n")

print("Q6. Orders to flag for manual review")
review = df[df["needs_review"]][["csv_line", "id", "order_date", "product",
                                 "region", "quantity", "price", "total",
                                 "review_reason"]]
print(review.to_string(index=False))
reasons = (df["review_reason"].str.split("; ").explode()
           .replace("", np.nan).dropna().value_counts())
print("\nreview reasons:\n", reasons.to_string())
print(f"-> {len(review)} of {len(df)} orders ({len(review) / len(df):.0%}).")

# ==========================================================================
# MISSION 5: repeatable pipeline checks
# ==========================================================================
section("MISSION 5 - PIPELINE GUARANTEES")
again, report_again = prepare_sales(raw)
pd.testing.assert_frame_equal(cleaned, again)
assert report == report_again
pd.testing.assert_frame_equal(raw, raw_snapshot)
print("raw DataFrame unchanged after the pipeline: OK")
print("running prepare_sales twice gives identical data and report: OK")
print("(unit tests: pytest -q test_sales_pipeline.py)")

# ==========================================================================
# BONUS A: quality_report before vs after
# ==========================================================================
section("BONUS - quality_report(), group-by and benchmark")
qr = quality_report(cleaned[["order_date", "product", "category", "region",
                             "quantity", "price", "channel", "total"]])
print("quality_report on the cleaned data:")
print(json.dumps(qr, indent=2, default=str))

# BONUS B: region x category
print("\nTotal sales and order counts by region x category")
grp = (df.groupby(["region", "category"])
         .agg(orders=("id", "count"), total_sales=("total", "sum"))
         .round(2))
print(grp.to_string())

# BONUS C: benchmark on 100,000 rows
print("\nBenchmark on 100,000 rows: vectorised vs apply(axis=1)")
big = df.sample(100_000, replace=True, random_state=0).reset_index(drop=True)


def timed(fn):
    t0 = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - t0


_, t_vec_total = timed(lambda: big["quantity"].astype("float64") * big["price"])
_, t_app_total = timed(lambda: big.apply(
    lambda r: float(r["quantity"]) * r["price"] if pd.notna(r["quantity"]) else np.nan,
    axis=1))
_, t_vec_label = timed(lambda: big["product"] + " x"
                       + big["quantity"].astype("string").fillna("?"))
_, t_app_label = timed(lambda: product_label_apply(big))
for name, tv, ta in [("total = quantity * price", t_vec_total, t_app_total),
                     ("product_label", t_vec_label, t_app_label)]:
    print(f"{name:26s} vectorised {tv * 1000:8.1f} ms | apply {ta * 1000:9.1f} ms "
          f"| apply is {ta / tv:6.0f}x slower")

# ==========================================================================
# VERDICT
# ==========================================================================
section("VERDICT - can management trust this dataset?")
n_rev, n = len(review), len(df)
# Rough size of what is missing: orders with a known quantity but no price,
# valued at the product's median price.  ONLY for judging materiality here;
# these numbers are never written into the cleaned data.
median_price = df.groupby("product")["price"].transform("median")
est_missing = (df["quantity"].astype("float64") * median_price)[
    df["price"].isna() & df["quantity"].notna()].sum()
flag_share = df.loc[df["needs_review"], "total"].sum() / total
print(f"""
Short answer: structurally yes, financially only with caveats.

What is now reliable
  * One row per order id ({report['rows_in']} rows in -> {n} out), consistent
    product / category / region / channel, real numbers and real dates.
  * Nothing was invented: {int(df['total'].isna().sum())} orders without a usable
    price or quantity have no total; they are NOT counted as 0.

What management should NOT take at face value
  * The total of {total:,.2f} is a LOWER BOUND: it omits those
    {int(df['total'].isna().sum())} orders.
  * {n_rev} of {n} orders ({n_rev / n:.0%}) carry a review flag and they hold
    {flag_share:.0%} of the known sales value (three 25-unit orders and the
    re-keyed ORD-0040 are among them).
  * Sales are concentrated: the single largest order ({top1['id']}, 20 units)
    is {top1['total'] / total:.0%} of the total and Electronics is
    {by_cat.iloc[0] / by_cat.sum():.0%}. It has a normal price and quantity so
    we did not flag it as an error, but it is worth about
    {top1['total'] / est_missing:.1f}x the rough value of all orders with a missing
    price (~{est_missing:,.0f} at median prices), so confirm it first.

Needs a human (sales ops / finance)
  1. Fill in the {int(df['price'].isna().sum())} missing prices and
     {int(df['quantity'].isna().sum())} missing/zero/negative quantities
     (negative or zero may be returns - decide how to book them).
  2. Confirm the currency of the 3 prices that arrived with $ / EUR symbols
     (no exchange rate was applied) and the price outliers (USB-C Hub at 349 and
     1299.99, Wireless Mouse at 331.55).
  3. Fix the {int(df['order_date'].isna().sum())} impossible dates and the 2027 date.
  4. Decide which ORD-0040 is right (we kept the newer, 27.10).
  5. Confirm product vs category on the {int(df['category_conflict'].sum())} mismatches
     (we trusted the product name).
  6. Check the quantities above {SUSPICIOUS_QTY} (25 units) are real bulk orders.
  7. Ask the source system why ids {', '.join(f'ORD-{g:04d}' for g in gap)} are missing.
""")

# Deliverable files
cleaned.to_csv(HERE / "clean_sales_cleaned.csv", index=False)
review.to_csv(HERE / "manual_review.csv", index=False)
print("written: clean_sales_cleaned.csv, manual_review.csv")
