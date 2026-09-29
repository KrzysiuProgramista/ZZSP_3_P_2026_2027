# Exercise 8: The messy import

The file contains:

- two junk lines before the real header,
- several representations of missing values,
- a price column containing a currency symbol,
- a date column in `DD.MM.YYYY` format,
- duplicate rows.

## Compact solution

```python
import pandas as pd

df = (pd.read_csv(
        "messy.csv",
        skiprows=2,
        na_values=["n/a", "-", "brak", ""],
        parse_dates=["date"],
        dayfirst=True
    )
    .assign(
        price=lambda x: pd.to_numeric(
            x["price"]
            .astype("string")
            .str.replace(r"[^0-9,.-]", "", regex=True)
            .str.replace(",", ".", regex=False),
            errors="coerce"
        )
    )
    .drop_duplicates()
    .reset_index(drop=True)
)
```

> If the columns in `messy.csv` use different names, replace `price` and `date` with the actual column names.

## Parameters and methods used

### `skiprows=2`

Skips the first two junk lines so that pandas uses the third line as the real CSV header.

### `na_values=["n/a", "-", "brak", ""]`

Treats all listed values as missing data (`NaN`).

### `parse_dates=["date"]`

Reads the `date` column as dates instead of strings.

### `dayfirst=True`

The dates are stored in `DD.MM.YYYY` format, so the day is interpreted before the month.

### `.assign(...)`

Cleans and converts the `price` column to a numeric dtype.

### `.drop_duplicates()`

Removes duplicate rows.

### `.reset_index(drop=True)`

Creates a clean sequential index.

## Check the result

```python
print(df.dtypes)
print(df.isna().sum())
print(df.duplicated().sum())
```

The final duplicate count should be `0`, `date` should be a datetime dtype, and `price` should be numeric.
