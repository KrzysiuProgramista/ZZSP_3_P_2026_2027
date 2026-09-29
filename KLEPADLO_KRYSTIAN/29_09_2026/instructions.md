# Pandas Data Handling Exercises

## Exercise 1: Basic CSV reading
Read the file `sales.csv` (in this folder) into a DataFrame called `sales_df`.
1. Print the first 5 rows, the shape and the dtypes.
2. Print the column names.
3. Print how much memory it uses (df.info(memory_usage="deep")).

## Exercise 2: The awkward file
Read `sales_pl.csv` (in this folder). It uses semicolons, comma decimals and Polish column names.
1. Read it correctly so that the numeric columns are numeric, not strings.
2. Rename the columns to English with df.rename(columns={...}).
3. Confirm with .dtypes that nothing is left as `object` that should be a number.

## Exercise 3: A first-pass inspection routine
Write a function `inspect(df)` that prints, for any DataFrame:
- the shape
- the column names with their dtypes
- the number and percentage of missing values per column
- the number of duplicate rows
- for numeric columns: min, max, mean, median
- for object columns: the number of unique values and the 3 most common
Test it on both files. You will reuse this function all year.

## Exercise 4: Reading JSON
1. Read `products.json` (in this folder).
2. Note that nested objects become dictionaries inside cells.
3. Flatten them with `pd.json_normalize`.
4. Compare the two results.

## Exercise 5: Writing files
1. Write your cleaned sales data to `sales_clean.csv` without the index.
2. Write it to JSON with `orient="records"` and look at the file.
3. Write it to Excel (you may need `pip install openpyxl`).
4. Read each one back and confirm you get the same data.