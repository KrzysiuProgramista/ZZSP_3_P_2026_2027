import numpy as np
import pandas as pd

from ex2 import print_quality_report, quality_report

INPUT_CSV = "dirty_sales.csv"
OUTPUT_CSV = "sales_clean.csv"

VAT_RATE = 1.23
BULK_THRESHOLD = 10
PRIORITY_HIGH = 5000
PRIORITY_MEDIUM = 1000

# A quantity above this is not impossible, only unusual for this shop, so it
# is flagged for a human instead of being removed.
SUSPICIOUS_QUANTITY = 20

# Why hard-coded tables and not "take the most frequent spelling"? A lookup
# table is auditable and gives the same answer on every export. Majority vote
# changes its mind as soon as the next dirty file arrives.
PRODUCTS = [
    "Office Chair", "Laptop Pro 14", "Wireless Mouse", "Notebook Pack",
    "Webcam HD", "Mechanical Keyboard", "Monitor 27", "Headphones",
    "USB-C Hub", "Desk Lamp", "Standing Desk", "Whiteboard",
]

# .str.title() cannot be used here: it would turn "USB-C Hub" into
# "Usb-C Hub" and "Webcam HD" into "Webcam Hd".
PRODUCT_MAP = {name.lower(): name for name in PRODUCTS}

CATEGORY_MAP = {c.lower(): c for c in
                ["Furniture", "Electronics", "Accessories", "Stationery"]}
REGION_MAP = {r.lower(): r for r in ["North", "South", "East", "West"]}
CHANNEL_MAP = {c.lower(): c for c in ["Phone", "Online", "Store"]}

REGION_CODES = {"North": "N", "South": "S", "East": "E", "West": "W"}

# The catalogue: which category each product really belongs to. Used only to
# FLAG mismatches - never to overwrite them, because we cannot know whether
# the product name or the category is the typo.
PRODUCT_CATEGORY = {
    "Office Chair": "Furniture", "Desk Lamp": "Furniture",
    "Standing Desk": "Furniture", "Laptop Pro 14": "Electronics",
    "Webcam HD": "Electronics", "Monitor 27": "Electronics",
    "Headphones": "Electronics", "Wireless Mouse": "Accessories",
    "Mechanical Keyboard": "Accessories", "USB-C Hub": "Accessories",
    "Notebook Pack": "Stationery", "Whiteboard": "Stationery",
}

MISSING_LITERALS = ["unknown", "n/a", "na", "none", "null", "-", "?", ""]


def profile_damage(df):
    """Print the diagnosis. Reads only; changes nothing."""
    print("=" * 78)
    print("MISSION 1 - PROFILE THE DAMAGE")
    print("=" * 78)
    print(f"shape: {df.shape[0]} rows x {df.shape[1]} columns\n")
    print("--- head() ---")
    print(df.head().to_string(index=False))

    print("\n--- dtypes (read with dtype=str, so everything is text) ---")
    print(df.dtypes.to_string())

    print("\n--- missing values per column ---")
    missing = pd.DataFrame({
        "missing": df.isna().sum(),
        "missing_pct": (df.isna().mean() * 100).round(1),
    })
    print(missing.to_string())

    print("\n--- duplicates ---")
    exact = int(df.duplicated().sum())
    repeated_ids = df.loc[df["id"].duplicated(keep=False), "id"]
    print(f"exact duplicate rows: {exact}")
    print(f"repeated id values: {sorted(repeated_ids.unique().tolist())}")
    for order_id in sorted(repeated_ids.unique().tolist()):
        print(f"\n  rows carrying id {order_id}:")
        print(df.loc[df["id"] == order_id].to_string(index=False))

    print("\n--- unique values in the label columns ---")
    for column in ["region", "category", "channel"]:
        values = sorted(df[column].dropna().unique().tolist())
        normalised = df[column].str.strip().str.lower().nunique()
        print(f"  {column}: {len(values)} spellings -> {normalised} real "
              f"values")
        print(f"    {values}")

    print("\n--- DATA-QUALITY ISSUES FOUND (eight, not four) ---")
    issues = [
        "price is text: '$1,299.99' (thousands comma), '€ 349,00' (DECIMAL "
        "comma), the literal 'unknown', and 4 blanks",
        "quantity is text: the word 'five', a negative -3, a zero, 2 blanks",
        "order_date holds 31.02.2026 twice - a date that does not exist",
        "order_date holds 05.12.2027 - in the future",
        "region has 7 spellings for 4 regions (' north ', 'NORTH', 'south')",
        "category has 6 spellings for 4 categories ('electronics', "
        "'Accessories ')",
        "product has 15 spellings for 12 products (' laptop pro 14 ', "
        "'WIRELESS MOUSE', 'desk LAMP')",
        "1 exact duplicate row (ORD-0026) and 1 repeated id with CONFLICTING "
        "data (ORD-0040, two different order dates)",
        "4 rows where the product does not belong to its category "
        "(e.g. 'Laptop Pro 14' filed under 'Accessories')",
    ]
    for number, issue in enumerate(issues, start=1):
        print(f"  {number}. {issue}")
    print()


def _parse_price(raw):
    """Text -> float. Returns (Series, issue Series, counts).

    DECISION: anything that cannot be read as a number becomes NaN, never 0.
    A zero price would quietly shrink every total and every average.
    """
    text = raw.astype("string").str.strip()

    blank = text.isna() | text.eq("").fillna(False)
    unknown = text.str.lower().isin(MISSING_LITERALS).fillna(False)
    had_symbol = text.str.contains(r"[$€£]", na=False)

    digits = text.str.replace(r"[^0-9.,\-]", "", regex=True)
    digits = digits.mask(blank | unknown, pd.NA).replace("", pd.NA)

    # Which separator is the DECIMAL point? The one that comes last, but a
    # comma followed by three digits is a thousands separator ("1,299"),
    # while a comma followed by one or two is decimal ("349,00").
    last_dot = digits.str.rfind(".")
    last_comma = digits.str.rfind(",")
    digits_after_comma = digits.str.len() - last_comma - 1
    comma_is_decimal = (
        last_comma.gt(last_dot) & digits_after_comma.between(1, 2)
    ).fillna(False)

    european = (digits.str.replace(".", "", regex=False)
                      .str.replace(",", ".", regex=False))
    anglo = digits.str.replace(",", "", regex=False)
    price = pd.to_numeric(anglo.where(~comma_is_decimal, european),
                          errors="coerce")

    # The reason a price is missing travels with the row, not just a count.
    unparseable = price.isna() & ~blank & ~unknown
    issue = pd.Series("", index=raw.index, dtype="string")
    issue = issue.where(~blank, "price blank in the export")
    issue = issue.where(~unknown,
                        "price exported as '" + text.fillna("") + "'")
    issue = issue.where(~unparseable, "price could not be parsed")

    counts = {
        "blank_to_nan": int(blank.sum()),
        "unknown_literal_to_nan": int(unknown.sum()),
        "currency_symbol_stripped": int(had_symbol.sum()),
        "decimal_comma_fixed": int(comma_is_decimal.sum()),
        "unparseable_to_nan": int(unparseable.sum()),
        "non_positive": int((price <= 0).fillna(False).sum()),
    }
    return price, issue, counts


def _parse_quantity(raw):
    """Text -> nullable Int64. Returns (Series, issue Series, counts).

    DECISIONS, and why:
      * ''      -> NA. Unknown is not zero.
      * 'five'  -> NA. Guessing 5 would invent data the export never had.
      * -3      -> NA + flagged. A negative quantity sold is impossible; it
                   is probably a return booked wrongly, so a human must look.
      * 0       -> KEPT as 0 + flagged. Zero is a legitimate value (cancelled
                   line), so deleting it would hide a real record. Its total
                   is 0, which is correct, not a guess.
    """
    text = raw.astype("string").str.strip()
    blank = text.isna() | text.eq("").fillna(False)

    numeric = pd.to_numeric(text, errors="coerce")
    non_numeric = (numeric.isna() & ~blank)
    negative = numeric.lt(0).fillna(False)
    zero = numeric.eq(0).fillna(False)

    quantity = numeric.mask(negative).astype("Int64")

    issue = pd.Series("", index=raw.index, dtype="string")
    issue = issue.where(~blank, "quantity blank in the export")
    issue = issue.where(~non_numeric,
                        "quantity written as text ('" + text.fillna("") + "')")
    issue = issue.where(~negative,
                        "quantity negative in the export ('"
                        + text.fillna("") + "')")
    issue = issue.where(~zero, "quantity is zero")

    counts = {
        "blank_to_nan": int(blank.sum()),
        "non_numeric_to_nan": int(non_numeric.sum()),
        "negative_to_nan": int(negative.sum()),
        "zero_kept": int(zero.sum()),
    }
    return quantity, issue, counts


def _canonical(raw, mapping, label):
    """Strip + lowercase as a lookup key, then map to the official spelling.

    Unmapped values become 'Unknown <label>' rather than disappearing, so a
    new spelling shows up in the report instead of being silently dropped.
    """
    text = raw.astype("string").str.strip()
    key = text.str.lower()
    canonical = key.map(mapping)

    unmapped = canonical.isna() & text.notna()
    canonical = canonical.where(~unmapped, f"Unknown {label}")
    canonical = canonical.fillna(f"Unknown {label}")

    counts = {
        # counted on the ORIGINAL text, before stripping, so that
        # "Accessories " and "Accessories" show up as two spellings
        "spellings_before": int(raw.nunique()),
        "values_after": int(canonical.nunique()),
        "renamed": int((text != canonical).fillna(True).sum()),
        "unmapped": int(unmapped.sum()),
    }
    return canonical.astype("string"), counts


def clean_sales(df, *, today=None):
    """Return (cleaned copy, report dict). `df` is never modified.

    `today` is the reference date for the "order in the future" check. It
    defaults to the current date but can be pinned so that tests and reruns
    are reproducible.
    """
    today = pd.Timestamp.today().normalize() if today is None \
        else pd.Timestamp(today)

    out = df.copy(deep=True)
    rows_before = len(out)
    report = {"rows_before": rows_before, "reference_date": str(today.date())}

    out["id"] = out["id"].astype("string").str.strip()
    for column, mapping, label in [
        ("product", PRODUCT_MAP, "product"),
        ("category", CATEGORY_MAP, "category"),
        ("region", REGION_MAP, "region"),
        ("channel", CHANNEL_MAP, "channel"),
    ]:
        out[column], report[column] = _canonical(out[column], mapping, label)

    out["price"], price_issue, report["price"] = _parse_price(out["price"])
    out["quantity"], quantity_issue, report["quantity"] = \
        _parse_quantity(df["quantity"])

    # DECISION: an impossible date (31.02.2026) becomes NaT and is flagged.
    # We do not snap it to 28.02 - that would be inventing a fact.
    out["order_date"] = pd.to_datetime(
        out["order_date"].astype("string").str.strip(),
        format="%d.%m.%Y", errors="coerce")
    report["order_date"] = {
        "invalid_to_nat": int(out["order_date"].isna().sum()),
        "in_the_future": int(out["order_date"].gt(today).fillna(False).sum()),
    }

    # The audit trail: why this row's price or quantity is missing. Empty
    # string means "nothing was wrong with it".
    out["price_issue"] = price_issue
    out["quantity_issue"] = quantity_issue

    # Done AFTER standardising, so two rows that differed only in casing or
    # whitespace are recognised as the same record.
    exact_duplicates = out.duplicated()
    report["exact_duplicates_dropped"] = int(exact_duplicates.sum())
    report["duplicate_ids_dropped"] = sorted(
        out.loc[exact_duplicates, "id"].tolist())
    out = out.loc[~exact_duplicates]

    # DECISION: keep the NEWEST order_date and flag the id. An id is supposed
    # to be unique, so a second row is a correction or a double export; the
    # later record is the better guess. Dropping it silently would be wrong,
    # so every affected id is listed in the report for manual review.
    conflicting = out.loc[out["id"].duplicated(keep=False), "id"]
    report["id_conflicts"] = sorted(conflicting.unique().tolist())
    out = (out.sort_values("order_date", na_position="first")
              .drop_duplicates(subset="id", keep="last")
              .sort_index())
    report["id_conflict_rows_dropped"] = (
        rows_before - report["exact_duplicates_dropped"] - len(out))

    report["rows_after"] = len(out)
    report["rows_dropped"] = rows_before - len(out)
    report["values_fixed"] = (
        report["price"]["currency_symbol_stripped"]
        + report["price"]["decimal_comma_fixed"]
        + sum(report[c]["renamed"] for c in
              ["product", "category", "region", "channel"])
    )
    report["missing_after"] = {
        column: int(out[column].isna().sum()) for column in out.columns
    }
    return out, report


REVIEW_RULES = [
    (lambda d, today: d["order_date"].isna(),
     "date impossible, stored as NaT"),
    (lambda d, today: d["order_date"].gt(today).fillna(False),
     "order dated in the future"),
    (lambda d, today: d["quantity"].gt(SUSPICIOUS_QUANTITY).fillna(False),
     f"quantity above {SUSPICIOUS_QUANTITY}, unusual for this shop"),
    (lambda d, today: d["category"].ne(d["product"].map(PRODUCT_CATEGORY))
                      & d["product"].map(PRODUCT_CATEGORY).notna(),
     "product does not belong to its category"),
    (lambda d, today: d["product"].str.startswith("Unknown").fillna(False),
     "product name not in the catalogue"),
]


ISSUE_COLUMNS = ["price_issue", "quantity_issue"]


def add_features(df, *, today=None):
    """Return a copy with the derived columns. `df` is never modified."""
    today = pd.Timestamp.today().normalize() if today is None \
        else pd.Timestamp(today)
    out = df.copy(deep=True)

    # NA propagates: a missing price gives a missing total, which is the
    # honest answer.
    out["total"] = (out["quantity"] * out["price"]).round(2)
    out["total_with_vat"] = (out["total"] * VAT_RATE).round(2)

    # Nullable boolean, so "we do not know" stays distinguishable from
    # "not bulk".
    out["is_bulk"] = out["quantity"].ge(BULK_THRESHOLD).astype("boolean")

    # The FIRST condition is the missing-total test, so rows without a
    # total are labelled "unknown" instead of falling into "low".
    total = out["total"]
    conditions = [
        total.isna().to_numpy(),
        total.ge(PRIORITY_HIGH).fillna(False).to_numpy(),
        total.ge(PRIORITY_MEDIUM).fillna(False).to_numpy(),
    ]
    out["priority"] = pd.Series(
        np.select(conditions, ["unknown", "high", "medium"], default="low"),
        index=out.index, dtype="string")

    # An unmapped region keeps an explicit code instead of becoming NaN.
    out["region_code"] = (out["region"].map(REGION_CODES)
                          .fillna("UNK").astype("string"))

    # A missing quantity shows as "x?" rather than "x<NA>".
    quantity_text = out["quantity"].astype("string").fillna("?")
    out["product_label"] = (out["product"].astype("string") + " x"
                            + quantity_text)

    reasons = pd.Series("", index=out.index, dtype="string")
    for column in ISSUE_COLUMNS:
        if column in out.columns:
            mask = out[column].ne("").fillna(False)
            reasons = reasons.where(~mask, reasons + "; " + out[column])
    for build_mask, label in REVIEW_RULES:
        mask = build_mask(out, today).fillna(False)
        reasons = reasons.where(~mask, reasons + f"; {label}")
    reasons = reasons.str.lstrip("; ")
    out["review_reasons"] = reasons
    out["needs_review"] = reasons.ne("").astype("boolean")
    return out


def prepare_sales(df, *, today=None):
    """Full pipeline: clean, enrich, report. `df` is never modified."""
    cleaned, report = clean_sales(df, today=today)
    enriched = add_features(cleaned, today=today)
    report["rows_flagged_for_review"] = int(
        enriched["needs_review"].fillna(False).sum())
    report["columns_added"] = [c for c in enriched.columns
                               if c not in df.columns]
    return enriched, report


def answer_management(sales, report):
    print("=" * 78)
    print("MISSION 4 - ANSWERS FOR MANAGEMENT")
    print("=" * 78)

    print("\nQ1. Which category has the highest total sales value?")
    by_category = (sales.groupby("category")["total"].sum()
                   .sort_values(ascending=False).round(2))
    print(by_category.to_string())
    top = by_category.index[0]
    share = by_category.iloc[0] / by_category.sum() * 100
    print(f"  -> {top}: {by_category.iloc[0]:,.2f} "
          f"({share:.1f}% of all sales).")
    print("     Driven by Laptop Pro 14 and Monitor 27 unit prices, not by")
    print("     order count. Orders with a missing price contribute nothing")
    print("     here, so this is a FLOOR, not the true value.")

    print("\nQ2. Which five orders have the highest total value?")
    top5 = (sales.nlargest(5, "total")
            [["id", "product", "quantity", "price", "total", "region"]])
    print(top5.to_string(index=False))
    print("  -> All five are Laptop Pro 14 / Monitor 27 bulk orders.")

    print("\nQ3. Which region has the most orders?")
    by_region = sales["region"].value_counts()
    print(by_region.to_string())
    leaders = by_region.index[by_region == by_region.max()].tolist()
    if len(leaders) == 1:
        print(f"  -> {leaders[0]} with {by_region.max()} orders.")
    else:
        # Do not hide a tie by printing whichever row sorted first.
        print(f"  -> A TIE: {' and '.join(leaders)}, {by_region.max()} "
              f"orders each.")
    print("     This is order COUNT, not value; Q1 shows the value is")
    print("     concentrated in Electronics instead.")

    print("\nQ4. How many orders are missing a usable price or quantity?")
    no_price = sales["price"].isna()
    no_quantity = sales["quantity"].isna()
    print(f"  missing price           : {int(no_price.sum())}")
    print(f"  missing quantity        : {int(no_quantity.sum())}")
    print(f"  missing either          : {int((no_price | no_quantity).sum())}")
    print(f"  -> {int((no_price | no_quantity).sum())} of {len(sales)} orders "
          f"({(no_price | no_quantity).mean() * 100:.1f}%) cannot produce a")
    print("     total. Their priority is 'unknown', not 'low'.")

    print("\nQ5. What is the total sales value after cleaning?")
    total_net = sales["total"].sum()
    total_vat = sales["total_with_vat"].sum()
    usable = int(sales["total"].notna().sum())
    print(f"  net (excl. VAT): {total_net:,.2f}")
    print(f"  gross (incl. 23% VAT): {total_vat:,.2f}")
    print(f"  computed from {usable} of {len(sales)} orders.")
    print("  -> HOW MISSING VALUES WERE HANDLED: excluded, not zero-filled.")
    print("     pandas .sum() skips NaN, so the figure is the value of the")
    print("     orders we can actually price. It UNDERSTATES real sales by")
    print(f"     whatever the {len(sales) - usable} orders without a usable")
    print("     total were worth (6 lack a price, 4 lack a quantity).")

    print("\nQ6. Which orders should be flagged for manual review?")
    flagged = sales.loc[sales["needs_review"].fillna(False)]
    print(f"  {len(flagged)} of {len(sales)} orders flagged. By reason:")
    reason_counts = (flagged["review_reasons"].str.split("; ")
                     .explode().value_counts())
    print(reason_counts.to_string())
    print("\n  the flagged orders:")
    print(flagged[["id", "order_date", "product", "category", "quantity",
                   "price", "review_reasons"]].to_string(index=False))
    print()


def benchmark_label(n=100_000, repeats=5):
    """Vectorised string concatenation vs apply(axis=1) on n rows."""
    import timeit

    rng = np.random.default_rng(0)
    big = pd.DataFrame({
        "product": rng.choice(PRODUCTS, size=n),
        "quantity": rng.integers(1, 30, size=n),
    })

    vectorised = timeit.timeit(
        lambda: big["product"].astype("string") + " x"
        + big["quantity"].astype("string"),
        number=repeats) / repeats
    row_wise = timeit.timeit(
        lambda: big.apply(
            lambda row: f"{row['product']} x{row['quantity']}", axis=1),
        number=repeats) / repeats

    print("=" * 78)
    print(f"BONUS - product_label on {n:,} rows (mean of {repeats} runs)")
    print("=" * 78)
    print(f"  vectorised .str concat : {vectorised * 1000:8.1f} ms")
    print(f"  apply(axis=1)          : {row_wise * 1000:8.1f} ms")
    print(f"  ratio                  : {row_wise / vectorised:8.1f}x slower")
    print("  Measured on this machine, this pandas version and this data.")
    print("  The ORDER of magnitude is the lesson, not the exact number.")
    print()
    return vectorised, row_wise


def group_summary(sales):
    print("=" * 78)
    print("BONUS - sales by region and category")
    print("=" * 78)
    summary = (sales.groupby(["region", "category"])
               .agg(orders=("id", "size"),
                    total_sales=("total", "sum"),
                    priced_orders=("total", "count"))
               .round(2))
    print(summary.to_string())
    print("\n  'orders' counts every row; 'priced_orders' counts the rows")
    print("  that had both a price and a quantity. Where they differ, the")
    print("  total_sales figure is incomplete for that cell.")
    print()


def verdict(sales, report):
    print("=" * 78)
    print("FINAL VERDICT - Can management trust this dataset?")
    print("=" * 78)

    rows = len(sales)
    flagged = int(sales["needs_review"].fillna(False).sum())
    priced = int(sales["total"].notna().sum())
    clean_rows = rows - flagged

    print(f"\nNo - not as a single number, and yes - for most of the rows.\n")
    print(f"  {report['rows_before']} rows in, {rows} rows out "
          f"({report['rows_dropped']} dropped: "
          f"{report['exact_duplicates_dropped']} exact duplicate, "
          f"{report['id_conflict_rows_dropped']} id conflict).")
    print(f"  {clean_rows} rows ({clean_rows / rows * 100:.0f}%) are clean "
          f"and usable without reservation.")
    print(f"  {flagged} rows ({flagged / rows * 100:.0f}%) carry at least one "
          f"flag.")
    print(f"  {priced} rows ({priced / rows * 100:.0f}%) have a usable total; "
          f"the reported sales value is a FLOOR.")

    print("\nSAFE TO SEND:")
    print("  * order counts per region, per category, per channel")
    print("  * the ranking of categories and the top-5 order list")
    print("  * the clean date range (August to October 2026)")

    print("\nNOT SAFE TO SEND WITHOUT A CAVEAT:")
    print(f"  * any absolute revenue figure - {rows - priced} orders have no")
    print("    price or no quantity, so every total is understated")
    print("  * averages per order, for the same reason")

    print("\nSTILL NEEDS HUMAN REVIEW (a machine cannot decide these):")
    print("  1. The 6 unpriced orders: was it free, or did the export fail?")
    print("     Only the source system knows. We refused to fill them with 0.")
    print("  2. ORD-0032 quantity 'five' - almost certainly 5, but writing 5")
    print("     would be us inventing data, so it stayed NaN.")
    print("  3. ORD-0094 quantity -3 - a return booked as a sale? Needs the")
    print("     original document.")
    print("  4. ORD-0022 quantity 0 - a cancelled line, or a bad export?")
    print("  5. ORD-0014 and ORD-0062 dated 31.02.2026 - which real date?")
    print("  6. ORD-0091 dated 05.12.2027 - a typo for 2026, or a pre-order?")
    print("  7. ORD-0040 appears twice with two different dates. We kept the")
    print("     newer one; someone must confirm that is the correct record.")
    print("  8. The 4 product/category mismatches (e.g. 'Laptop Pro 14' "
          "filed")
    print("     under 'Accessories'). We FLAGGED them and changed nothing,")
    print("     because we cannot tell which of the two fields is wrong -")
    print("     and the choice moves money between category totals.")
    print("\nThe pipeline is reproducible: prepare_sales() on the same input")
    print("gives byte-identical output, and never touches the raw frame.")
    print()


def main():
    raw = pd.read_csv(INPUT_CSV, dtype=str)
    untouched = raw.copy(deep=True)

    profile_damage(raw)

    print("=" * 78)
    print("BONUS - quality_report() on the RAW file")
    print("=" * 78)
    print_quality_report(quality_report(raw, INPUT_CSV))

    # Pin the reference date so this run is reproducible.
    sales, report = prepare_sales(raw, today="2026-11-03")

    print("=" * 78)
    print("MISSION 2 + 5 - CLEANING REPORT")
    print("=" * 78)
    for key, value in report.items():
        print(f"  {key}: {value}")
    print()

    print("=" * 78)
    print("MISSION 3 - DERIVED COLUMNS (first 10 rows)")
    print("=" * 78)
    print(sales[["id", "product", "quantity", "price", "total", "is_bulk",
                 "priority", "region_code", "product_label"]]
          .head(10).to_string(index=False))
    print("\n  priority distribution:")
    print(sales["priority"].value_counts().to_string())
    print()

    answer_management(sales, report)
    group_summary(sales)
    benchmark_label()

    pd.testing.assert_frame_equal(raw, untouched)
    again, _ = prepare_sales(raw, today="2026-11-03")
    pd.testing.assert_frame_equal(sales, again)
    print("Contract checks passed: raw input unchanged, pipeline "
          "reproducible.\n")

    verdict(sales, report)

    sales.to_csv(OUTPUT_CSV, index=False)
    print(f"Written: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()