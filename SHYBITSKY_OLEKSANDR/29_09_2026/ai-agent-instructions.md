# Pandas / NumPy AI Rules

Rules for AI assistants writing code that works with tabular datasets and data files.
Priority levels: **MUST** (always), **SHOULD** (default, deviate only with a reason), **AVOID** (anti-patterns), **VERIFY** (checks before declaring the task done).

## 0. Behavior of the AI

- MUST state assumptions explicitly (separator, encoding, decimal mark, date format, handling of missing values, sheet name).
- MUST NOT guess the format of an unknown file. Inspect it first (`head`, first bytes, `nrows=5`) or ask the user.
- MUST report every change that alters the data: rows dropped, values filled, columns renamed, types converted (with counts).
- MUST NOT silently change indexes, column names, or data types of existing data. If a change is needed, do it visibly and mention it.
- SHOULD prefer the simplest solution that is readable and correct over a clever one-liner.
- SHOULD mention the pandas version the code targets when behavior depends on it (e.g. Copy-on-Write, which is the default in pandas 3.0).

## 1. MUST

### Structures and naming
- MUST use `pandas` for tabular data. Use `DataFrame` as the main structure.
- MUST use NumPy only where pandas is not sufficient or NumPy is clearly simpler (vectorized math, `np.where`, `np.select`, random generators).
- MUST use clear, meaningful names for variables, aliases, and functions (`sales_df`, `monthly_totals`), not `x`, `tmp`, `df2`.
- MUST follow the naming convention already present in the dataset. For columns created by the AI, use one consistent style (default: `snake_case`, e.g. `order_date`, `location`, `temperature_c`).
- MUST prefer vectorized pandas operations over Python loops.
- MUST use `.loc` for label- and condition-based selection and `.iloc` for position-based selection.
- MUST modify data through a single `.loc[rows, column] = value` or `.assign()`, never through chained indexing (`df['a']['b'] = x`).
- MUST preserve meaningful indexes unless there is a reason to change them.

### File I/O
- MUST use the reader/writer that matches the file format:
  - `pd.read_csv()` / `to_csv()` for `.csv`, `.tsv`, `.txt` (for TSV set `sep='\t'`; for other delimiters set `sep` explicitly).
  - `pd.read_excel()` / `to_excel()` for `.xlsx`, `.xls`.
  - `pd.read_json()` / `to_json()` for `.json`; for JSON Lines use `lines=True` (and `orient='records'` when writing).
  - `pd.read_parquet()`, `pd.read_feather()`, `pd.read_sql()` for their formats.
- MUST set `encoding` explicitly when reading or writing text files (`.csv`, `.tsv`, `.txt`): `encoding='utf-8'`, or `'utf-8-sig'` for CSV meant to be opened in Excel.
- MUST write JSON with `force_ascii=False` so non-ASCII characters (e.g. Polish diacritics) are not escaped to `\uXXXX`. Note: `to_json()` has no `encoding` parameter; it writes UTF-8.
- MUST build paths with `pathlib.Path`. No hardcoded absolute or OS-specific paths.
- MUST NOT overwrite original source files. Write results to a new file, or create a backup and get explicit user confirmation first.
- MUST NOT call `pd.read_pickle()` on untrusted files (arbitrary code execution).
- MUST use parameterized queries with `pd.read_sql()` (`params=...`), never f-strings with user input.

## 2. SHOULD

### Operations
- SHOULD use `.isin()` for membership filtering, `sort_values()` / `sort_index()` for sorting.
- SHOULD reference columns by name, not by position.
- SHOULD use `.copy()` when a derived DataFrame will be modified independently, and never mutate a DataFrame passed into a function (return a new one).
- SHOULD prefer `.assign()`, `.pipe()`, and method chaining for multi-step transformations, as long as each step stays readable. Split long chains into named intermediate steps.
- SHOULD avoid `inplace=True`; assign the result instead.
- SHOULD use `.at` / `.iat` only for single-value access where performance matters.
- SHOULD prefer `np.where`, `np.select`, `.map`, `.str`, `.dt` over `.apply(axis=1)`. Use `.apply(axis=1)` only as a last resort.
- SHOULD use `np.isclose` (not `==`) for comparing floating-point numbers.
- SHOULD make randomness reproducible: `rng = np.random.default_rng(seed)` and `random_state=seed` in pandas/sklearn calls.
- SHOULD add type hints and a short docstring to reusable loading and processing functions.

### Reading and writing files
- SHOULD specify `sheet_name` explicitly when reading Excel files.
- SHOULD specify `engine` when the choice is not obvious (e.g. `engine='openpyxl'` for `.xlsx`).
- SHOULD specify `dtype={...}` and `parse_dates=[...]` on read, and `usecols=[...]` to load only the required columns.
- SHOULD read identifier-like columns as text (`dtype=str`): postal codes, PESEL, NIP, phone numbers, product codes, anything with leading zeros.
- SHOULD control missing-value parsing with `na_values` and `keep_default_na` when strings such as `"NA"` or `"N/A"` can be real values.
- SHOULD test loading logic on a sample (`nrows=`) before reading a large file in full.
- SHOULD handle JSON `orient` intentionally (`'records'`, `'split'`, ...) based on the data structure.
- SHOULD set `index=False` when exporting to CSV/Excel unless the index carries meaning.
- SHOULD prefer Parquet or Feather for intermediate files (keeps dtypes, smaller, faster than CSV).
- SHOULD consider `chunksize` or a scalable tool (Polars, Dask, DuckDB) when data does not fit comfortably in memory.
- SHOULD use `pd.ExcelWriter` for multi-sheet Excel output, and remind the user that formulas and custom formatting in an existing workbook are not preserved by pandas.

### Regional and Excel-related formats
- SHOULD check for typical European/Excel CSV conventions when parsing looks wrong: `sep=';'`, `decimal=','`, `thousands=' '`, and legacy encodings such as `cp1250` / `windows-1250` or `iso-8859-2`.
- SHOULD write Excel-friendly CSV with `encoding='utf-8-sig'` and, when the target uses the semicolon convention, `sep=';'` and `decimal=','`.

### Data cleaning
- SHOULD clean column names when they come from external files (`df.columns = df.columns.str.strip()`), and tell the user if names were changed.
- SHOULD convert dates with `pd.to_datetime(..., format=..., errors=...)` and set `dayfirst` and time zones explicitly.
- SHOULD check duplicates with `duplicated()` and choose `drop_duplicates(subset=...)` columns deliberately.
- SHOULD, before `merge`, check key uniqueness and use `validate=` (e.g. `'one_to_one'`, `'many_to_one'`) and, when diagnosing, `indicator=True`.
- SHOULD treat missing values as a decision, not a default: state whether they are dropped, filled, or kept, and count the affected rows.

## 3. AVOID

- AVOID `iterrows()` / `itertuples()` and other row-by-row loops when a vectorized alternative exists.
- AVOID chained indexing when assigning values.
- AVOID hard-coded column positions when column names are available.
- AVOID unnecessary DataFrame → NumPy → DataFrame conversions.
- AVOID NumPy where a simpler pandas operation is clearer.
- AVOID unnecessary one-liners that reduce readability.
- AVOID silent `fillna()` / `dropna()` / `astype()` / `drop_duplicates()` without reporting the effect.
- AVOID loading a whole huge dataset when only a subset or a chunk is needed.
- AVOID relying on default text encodings or default delimiters when the source is unknown.
- AVOID `inplace=True`.
- AVOID writing intermediate results over source files.

## 4. VERIFY

### Data integrity
- VERIFY the result has the expected columns (`df.columns`) and dtypes (`df.dtypes`, `df.info()`).
- VERIFY the row count after every filter, merge, concat, or drop (`df.shape`), and that it matches expectations (e.g. no row multiplication after a join).
- VERIFY missing values (`df.isna().sum()`) before and after transformations.
- VERIFY the index is preserved or was changed intentionally.
- VERIFY that assignments changed only the intended rows and columns.
- VERIFY date columns are `datetime64` and numeric columns are numeric, not `object`.
- VERIFY key columns are unique when they are supposed to be (`df['id'].is_unique`).
- VERIFY sanity constraints with `assert` where possible (value ranges, allowed categories, no negative quantities).

### Files
- VERIFY input files exist and are readable (`Path.exists()`, `Path.is_file()`) before opening them.
- VERIFY delimiter, quote character, decimal mark, header row, and encoding were parsed correctly (inspect `head()`, check there is no mojibake such as `Ä…` or `Å‚`, and that the data is not stuffed into a single column).
- VERIFY exported files can be read back with the same settings, and compare with the original (`pd.testing.assert_frame_equal`, allowing for intended dtype differences).
- VERIFY that identifiers with leading zeros survived the round trip.

### Code quality
- VERIFY the final code is readable, logically consistent, and free of unused variables and imports.
- VERIFY the code runs from top to bottom on a fresh interpreter, when it is possible to execute it.

## 5. Quick reference: read functions

### Basic calls

```python
import pandas as pd

# Minimal forms (always add an explicit encoding, see section 1)
sales_df = pd.read_csv("sales.csv", encoding="utf-8")
sales_df = pd.read_csv("sales.csv", sep=";", encoding="utf-8", decimal=",")
data_df = pd.read_json("data.json", encoding="utf-8")
report_df = pd.read_excel("report.xlsx", sheet_name="Q1")
```

### Typical Polish / Excel CSV with the important parameters

```python
from pathlib import Path
import pandas as pd

csv_path = Path("data") / "sales.csv"

sales_df = pd.read_csv(
    csv_path,
    sep=";",
    decimal=",",
    thousands=" ",
    encoding="utf-8-sig",          # or "cp1250" / "iso-8859-2" for legacy files
    header=0,
    usecols=["order_date", "postcode", "amount"],
    dtype={"postcode": str},
    parse_dates=["order_date"],
    date_format="%d.%m.%Y",
    na_values=["brak", "-", "n/a"],
)

report_df = pd.read_excel("report.xlsx", sheet_name="Q1", engine="openpyxl")
json_df = pd.read_json("data.json", orient="records", encoding="utf-8")
jsonl_df = pd.read_json("data.jsonl", lines=True, encoding="utf-8")
```

### The parameters that actually matter

| Parameter | Purpose |
|---|---|
| `sep` | The separator. Polish exports often use `;`. |
| `decimal` | `,` in Polish-locale files. |
| `thousands` | Thousands separator, often a space (sometimes a non-breaking space `\xa0`, which needs separate cleaning). |
| `encoding` | `utf-8`; `utf-8-sig` for Excel CSV with BOM (otherwise the first column may be named `\ufeffId`); `cp1250` or `iso-8859-2` (alias `latin2`) for older Polish files. |
| `header` | Which row holds the column names, or `None` if there is no header row. |
| `names` | Supply your own column names. If the file already has a header row, combine with `header=0` so the old header is not read as data. |
| `usecols` | Read only some columns. Much faster and lighter on big files. |
| `nrows` | Read only the first n rows, for a quick look. |
| `skiprows`, `skipfooter` | Skip titles or summary rows in reports (`skipfooter` requires `engine="python"`). |
| `na_values` | Extra strings to treat as missing, e.g. `["brak", "-", "n/a"]`. Added to the defaults. |
| `keep_default_na` | Set to `False` to switch off default missing-value strings (e.g. when `"NA"` is real data). |
| `parse_dates`, `date_format` | Parse these columns as dates, with an explicit format such as `"%d.%m.%Y"` (pandas 2.0+). |
| `dtype` | Force a column's type, e.g. `{"postcode": str}`. Also use for PESEL, NIP, and any ID with leading zeros. |
| `on_bad_lines`, `quotechar` | Handle malformed rows and quoting problems in CSV. |
| `sheet_name` | Excel sheet by name or index; `None` reads all sheets into a dict. |
| `lines`, `orient` | JSON Lines and the JSON layout. |

### Diagnosing an unknown CSV

- `sep=None, engine="python"` lets pandas sniff the delimiter. It is slower, so use it to identify the format, then set `sep` explicitly.
- Combine with `nrows=5` and check `df.shape` and `df.head()` to confirm the parse looks right.
