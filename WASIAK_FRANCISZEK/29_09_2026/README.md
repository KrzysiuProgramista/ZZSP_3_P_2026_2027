# Pandas: Reading, Inspecting, and Writing Files

## Directory and setup

Keep `README.md`, `exercises.py`, `sales.csv`, `sales_pl.csv`, `products.json`, `messy.csv`, and `Titanic-Dataset.csv` together in:

```text
WASIAK_FRANCISZEK/29_09_2026/
```

From the repository root, activate your virtual environment and install the dependencies:

```bash
source .venv/bin/activate
python -m pip install pandas openpyxl
cd WASIAK_FRANCISZEK/29_09_2026
python exercises.py
```

If your terminal already shows `(.venv)`, skip activation. If you are already in `29_09_2026`, run only `python exercises.py` rather than repeating the directory path. The script reads input files from the directory containing `exercises.py`.

The Titanic file comes from the [Kaggle Titanic dataset](https://www.kaggle.com/datasets/yasserh/titanic-dataset). Download and extract it as `Titanic-Dataset.csv`; the script looks for that exact name. If you have a file named `.xls`, check its actual format before deciding whether to rename it or read it as Excel.

## Exercises 1–5: Reading and inspection

### Exercise 1 — Basic CSV reading

Read `sales.csv` into `sales_df` with `pd.read_csv`. Print its first five rows (`.head()`), shape (`.shape`), dtypes (`.dtypes`), column names (`.columns.tolist()`), and detailed memory usage (`.info(memory_usage="deep")`). The supplied file contains 15 rows and 6 columns.

### Exercise 2 — Polish CSV

Read `sales_pl.csv` using semicolon-separated fields and comma decimals:

```python
sales_pl_df = pd.read_csv("sales_pl.csv", sep=";", decimal=",")
```

Rename the headers using `.rename(columns={...})`:

| Original header | English header |
|---|---|
| `data` | `date` |
| `produkt` | `product` |
| `kategoria` | `category` |
| `region` | `region` |
| `ilosc` | `quantity` |
| `cena_jednostkowa` | `unit_price` |

Check `.dtypes`: `quantity` should be numeric (`int64` in the supplied file) and `unit_price` should be numeric (`float64`). Text fields can correctly appear as `str` in pandas 3 or `object` in older pandas versions. The Polish file has 8 rows; it is not identical to `sales.csv`.

### Exercise 3 — Reusable inspection function

`inspect(df)` prints the shape; each column and dtype; missing count and percentage per column; duplicate-row count; numeric minimum, maximum, mean, and median; and unique counts plus the three most common values for text/object columns. Test it on `sales_df` and `sales_pl_df`.

To handle pandas 3 text columns, select both string and object dtypes:

```python
text_columns = df.select_dtypes(include=["object", "string"]).columns
if len(text_columns) == 0:
    print("No text/object columns")
```

Do not use `if not text_columns`: pandas does not allow a whole Index to be interpreted as one Boolean value.

### Exercise 4 — Reading JSON

Read `products.json` with `pd.read_json`. The `supplier` cells contain dictionaries and the `tags` cells contain lists. Load the JSON as Python data and call `pd.json_normalize` to turn supplier fields into `supplier.name` and `supplier.country` columns. Compare the original and flattened DataFrames. The tags remain lists unless you expand them separately.

### Exercise 5 — Writing files

Export the cleaned Polish sales DataFrame to `sales_clean.csv` (`index=False`), `sales_clean.json` (`orient="records"`), and `sales_clean.xlsx` (`index=False`). Inspect the JSON file, read all three exports back, and compare them with `pd.testing.assert_frame_equal`. The script parses the date column consistently before exporting and after importing.

## Exercise 6: Only what you need

The supplied `sales.csv` does not contain `amount`. The script first calculates `amount = quantity * unit_price` and saves `sales_with_amount.csv`. It then reads only `date`, `product`, and `amount` with `usecols`, and only the first 10 rows with `nrows=10`.

It also times full-column and selected-column reads with `time.perf_counter` over 100 repetitions. Because there are only 15 rows, these timings are illustrative rather than a meaningful performance benchmark.

## Exercise 7: Titanic dataset

Place `Titanic-Dataset.csv` beside `exercises.py` and run the script. Exercise 7 calls `inspect(titanic_df)`, lists five answerable questions, calculates answers to the first two, and identifies two questions that need additional data. If the file is absent, the script displays a message and continues to Exercise 8; that does not count as completing Exercise 7.

Five questions the dataset can answer:

1. What percentage of recorded passengers survived?
2. How did survival rates vary by sex?
3. How did survival rates vary by passenger class?
4. How did survival rates vary by age?
5. How did survival rates vary by embarkation port?

Answers calculated in the successful run:

- Overall survival: **38.38%**.
- Survival by sex: **74.20% for female passengers** and **18.89% for male passengers**.

These are descriptive rates for the rows in this dataset; they do not establish what caused survival.

Two questions the dataset cannot answer:

- What was each passenger's occupation? Occupation records are missing.
- Which lifeboat did each passenger board? Lifeboat assignment records are missing.

## Exercise 8: Messy import

Read `messy.csv` into a DataFrame with numeric prices, nullable integer quantities, parsed dates, standardized missing values, and no exact duplicate rows.

| Parameter or method | Purpose |
|---|---|
| `sep=";"` | Separates semicolon-delimited fields. |
| `skiprows=2` | Skips the two junk lines before the real header. |
| `na_values=["n/a", "-", "brak", ""]` | Recognizes the missing-value markers. |
| `parse_dates=["order_date"]` | Parses `order_date` during import. |
| `date_format="%d.%m.%Y"` | Specifies day.month.year dates. |
| `converters={"price": price_to_float}` | Removes `PLN` and thousands spaces, changes decimal commas to dots, and converts prices to floats. |
| `dtype={"id": "Int64", "name": "string", "quantity": "Int64", "notes": "string"}` | Uses nullable integers and string columns. |
| `.drop_duplicates(ignore_index=True)` | Drops exact repeated rows and resets the index. |

With the supplied file, the cleaned result has **8 rows and 0 duplicate rows**, with one missing price, one missing quantity, and five missing notes. Two Laptop purchases have different IDs and therefore remain separate; the repeated row with ID 4 is removed.

## Generated files

Running `exercises.py` writes `sales_clean.csv`, `sales_clean.json`, `sales_clean.xlsx`, and `sales_with_amount.csv` in the same directory.