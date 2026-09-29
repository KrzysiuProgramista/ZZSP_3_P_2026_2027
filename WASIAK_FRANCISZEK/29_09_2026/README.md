# Pandas: reading, inspecting, and writing files

## Directory

This exercise belongs in:

```text
WASIAK_FRANCISZEK/29.09.2026/
```

This directory contains this guide, `exercises.py`, and all supplied input files.

## Install packages

Open a terminal in the project directory and run:

```bash
python -m pip install pandas openpyxl
```

Then run the solution:

```bash
python exercises.py
```

## Exercise 1 — Basic CSV reading

Read `sales.csv` into a DataFrame named `sales_df`. Print:

- The first 5 rows with `.head()`
- The shape with `.shape`
- Data types with `.dtypes`
- Column names with `.columns.tolist()`
- Detailed memory usage with `.info(memory_usage="deep")`

## Exercise 2 — Polish CSV

`sales_pl.csv` uses semicolons (`;`) as separators and commas (`,`) as decimal separators. Read it using:

```python
pd.read_csv("sales_pl.csv", sep=";", decimal=",")
```

Rename the columns to English:

| Polish | English |
|---|---|
| `data` | `date` |
| `produkt` | `product` |
| `kategoria` | `category` |
| `region` | `region` |
| `ilosc` | `quantity` |
| `cena_jednostkowa` | `unit_price` |

Check `.dtypes`. `quantity` should be `int64`, and `unit_price` should be `float64`. Text fields correctly remain `object`.

## Exercise 3 — Reusable inspection function

`inspect(df)` prints:

- Shape
- All column names and dtypes
- Missing-value count and percentage for every column
- Number of duplicate rows
- For numeric columns: minimum, maximum, mean, and median
- For object columns: number of unique values and three most common values

The function is called for both sales DataFrames.

## Exercise 4 — JSON

`pd.read_json("products.json")` reads `supplier` as dictionaries inside cells and `tags` as lists inside cells. `pd.json_normalize(...)` expands dictionary values into separate columns: `supplier.name` and `supplier.country`.

The `tags` data remains a list, because it is not automatically expanded by `json_normalize`.

## Exercise 5 — Export files

The cleaned Polish sales DataFrame is exported as:

- `sales_clean.csv` — without an index
- `sales_clean.json` — `orient="records"`
- `sales_clean.xlsx` — without an index

The script reads each exported file back and checks it against the original cleaned DataFrame with `pd.testing.assert_frame_equal`.

`messy.csv` is provided but is not used in exercises 1–5.
