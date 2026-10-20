# 01 - Reading and writing files with pandas

Five exercises on getting data *into* a DataFrame and back *out* to disk.
Everything you need is in this folder.

## Setup

```bash
cd /Users/tymon/Dev/Python/cwel
python3 -m venv .venv
source .venv/bin/activate
pip install pandas openpyxl
```

`exercises.py` holds worked solutions for all five exercises - run it with
`python exercises.py` from inside this folder (the relative filenames need
that). Read a section, then try to rewrite it from the task description
below without looking; that is where the learning happens.

## The data files

| File | What is awkward about it |
|---|---|
| `sales.csv` | Nothing. Plain comma-separated, 15 rows. |
| `sales_pl.csv` | Semicolon separator, comma decimals, Polish column names. |
| `products.json` | Nested objects and lists inside the records. |
| `messy.csv` | Comment lines, currency strings, `n/a` / `-` markers, duplicates, `DD.MM.YYYY` dates. Not used until exercise 3, but look at it. |

---

## Exercise 1 - Basic CSV reading

Read `sales.csv` into a DataFrame called `sales_df`.

1. Print the first 5 rows, the shape and the dtypes.
2. Print the column names.
3. Print how much memory it uses (`df.info(memory_usage="deep")`).

Look at what dtype `date` got. Is it what you want?

## Exercise 2 - The awkward file

Read `sales_pl.csv`. It uses semicolons, comma decimals and Polish column names.

1. Read it correctly so that the numeric columns are numeric, not strings.
2. Rename the columns to English with `df.rename(columns={...})`.
3. Confirm with `.dtypes` that nothing is left as `object` that should be a number.

Hints: `sep=`, `decimal=`, `parse_dates=`.

## Exercise 3 - A first-pass inspection routine

Write a function `inspect(df)` that prints, for any DataFrame:

- the shape
- the column names with their dtypes
- the number and percentage of missing values per column
- the number of duplicate rows
- for numeric columns: min, max, mean, median
- for object columns: the number of unique values and the 3 most common

Test it on both files. You will reuse this function all year.

Hints: `df.isna().sum()`, `df.duplicated().sum()`,
`df.select_dtypes(include="number")`, `df[col].value_counts().head(3)`.

## Exercise 4 - Reading JSON

1. Read `products.json`.
2. Note that nested objects become dictionaries inside cells.
3. Flatten them with `pd.json_normalize`.
4. Compare the two results - column names, dtypes, what happened to `tags`.

## Exercise 5 - Writing files

1. Write your cleaned sales data to `sales_clean.csv` without the index.
2. Write it to JSON with `orient="records"` and look at the file.
3. Write it to Excel (needs `openpyxl`).
4. Read each one back and confirm you get the same data.

For step 4, `df.equals(df_roundtripped)` is the honest check. If it returns
`False`, find out which column changed and why - that is the real lesson of
this exercise.

Output files (`sales_clean.*`) belong in this folder; they are yours to
overwrite freely.
