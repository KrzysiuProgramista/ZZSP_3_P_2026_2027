# DATA RESCUE: The Sales Data Emergency

## Scenario
A retail company is about to send its monthly sales report to management, but the exported data is unreliable. Prices have inconsistent formats, some values are missing, product and region names are inconsistent, and duplicate or impossible records may be present. Your team has been hired to rescue the dataset.

**Input file:** `dirty_sales.csv`
**Tools:** Python, pandas, NumPy, pytest (tests are an extension if time is limited).
**Important:** Keep the raw DataFrame unchanged. Build your pipeline on a copy. Do not silently replace every missing value with zero. For each cleaning decision, add a short comment explaining why.

## Mission 1 — Profile the damage (10–15 min)
1. Load the CSV and inspect `head()`, `shape`, and `dtypes`.
2. Report missing values and missing percentages per column.
3. Find exact duplicate rows and repeated `id` values.
4. Inspect unique values in `region`, `category`, and `channel`.
5. Identify at least four different data-quality issues.

## Mission 2 — Clean the raw columns (20–25 min)
Write `clean_sales(df)` that returns a **cleaned copy**. It should:
1. Strip whitespace from strings.
2. Standardise `product`, `category`, `region`, and `channel` values.
3. Convert `price` to a numeric dtype. Handle currency symbols, thousands separators, decimal commas, blank strings, and `unknown`. Invalid or missing prices should become `NaN`, not zero.
4. Convert `quantity` to nullable integer `Int64`. Decide what to do with blank, non-numeric, zero, and negative quantities, and explain the choice.
5. Parse `order_date` as a datetime, handling the `DD.MM.YYYY` format and invalid dates.
6. Remove exact duplicate rows. For repeated `id` values, decide whether to keep the newest record or flag the conflict. Document your decision.
7. Return the cleaned DataFrame and a report dictionary with counts of dropped rows, fixed values, and remaining missing values.

## Mission 3 — Create useful columns (15–20 min)
Using vectorised operations wherever possible:
1. Add `total = quantity * price`.
2. Add `total_with_vat = total * 1.23`.
3. Add `is_bulk`, True when quantity is at least 10.
4. Add `priority` using `np.select`: `high` when total >= 5000, `medium` when total >= 1000, otherwise `low`. Missing totals should remain clearly identifiable.
5. Add a `region_code` column using `.map()` with a dictionary. Handle unknown regions.
6. Add a `product_label` column combining product and quantity. Compare vectorised string concatenation with `apply(axis=1)`; do not use `iterrows()`.

## Mission 4 — Ask management questions (15 min)
Use Pandas to answer each question with code and a short interpretation:
1. Which category has the highest total sales value?
2. Which five orders have the highest total value?
3. Which region has the most orders?
4. How many orders are missing a usable price or quantity?
5. What is the total sales value after cleaning? State how missing values were handled.
6. Which orders should be flagged for manual review? Include invalid dates, missing key values, and suspicious quantities.

## Mission 5 — Build a repeatable pipeline (15–20 min)
Write `prepare_sales(df)` that:
- does not modify the input DataFrame;
- calls your cleaning logic;
- creates the derived columns;
- returns `(cleaned_df, report)`;
- gives the same result when run twice on the same input.

Write at least **5 pytest tests**. Include tests for: input unchanged, correct numeric conversion, duplicate handling, derived total, and invalid/missing data.

## Final deliverable
Submit:
1. `analysis.py` or a notebook with clear section headings;
2. `clean_sales()` and `prepare_sales()`;
3. your quality report and answers to management;
4. tests;
5. a short verdict: **Can management trust this dataset? What still needs human review?**

## Rules
- Do not use loops over DataFrame rows to create columns.
- Prefer vectorised operations, `np.where` / `np.select`, `.map`, and `.str` methods.
- Use `.apply()` only when it genuinely improves clarity.
- Do not use `inplace=True` as a shortcut for pipeline design.
- A cleaning decision must be explained, not merely coded.

## Bonus challenges
- Benchmark a vectorised transformation against `apply(axis=1)` on 100,000 rows.
- Add a `quality_report(df)` that reports dtypes, missing percentages, unique values, duplicates, numeric ranges, and suspicious outliers.
- Group results by `region` and `category`; report total sales and order counts.