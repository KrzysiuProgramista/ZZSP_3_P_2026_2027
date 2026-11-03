# pandas — Instructions for AI/LLM Agents

> Source basis: "10 minutes to pandas" (pandas 3.0.6 docs) + pandas 3.0 release notes.
> Target: **pandas ≥ 3.0**. If the environment runs pandas 2.x, check `pd.__version__` first and note the differences flagged ⚠️ below.

---

## 0. Ground rules for the agent

1. **Check the version before writing non-trivial code:** `import pandas as pd; print(pd.__version__)`. Behaviour of strings, copies and datetimes differs between 2.x and 3.x.
2. **Inspect before transforming.** Before any operation on unfamiliar data, run `df.shape`, `df.dtypes`, `df.head()`, `df.isna().sum()`. Never assume column names or dtypes.
3. **Vectorize.** Use column operations, `.str`, `.dt`, `groupby`, `merge`. Do not loop over rows (`iterrows`, `for i in range(len(df))`) unless there is no vectorized alternative.
4. **Be explicit in production code:** use `.loc` / `.iloc` / `.at` / `.iat` rather than bare `[]` chains.
5. **Do not invent APIs.** If unsure whether a method/argument exists in 3.x, check `help(pd.DataFrame.method)` or the docs rather than guessing.

Standard imports:

```python
import numpy as np
import pandas as pd
```

---

## 1. Core data structures

| Class | What it is |
|---|---|
| `pd.Series` | 1-D labeled array, single dtype |
| `pd.DataFrame` | 2-D table, **one dtype per column** (NumPy array has one dtype for the whole array) |

```python
s = pd.Series([1, 3, 5, np.nan, 6, 8])                      # default RangeIndex
dates = pd.date_range("20130101", periods=6)                  # DatetimeIndex
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))
df2 = pd.DataFrame({"A": 1.0, "B": pd.Timestamp("20130102"),
                    "E": pd.Categorical(["test", "train"] * 2), "F": "foo"})
```

`df.to_numpy()` picks a common dtype for all columns; mixed dtypes → `object` array and a copy. Prefer working in pandas; convert to NumPy only at the boundary.

---

## 2. pandas 3.x changes the agent MUST respect

### 2.1 Copy-on-Write (CoW) is the only mode ⚠️
- Every result of indexing or a method **behaves as a copy**. Modifying it never modifies the parent.
- **Chained assignment never works** and must not be generated:

  ```python
  # WRONG — silently does nothing to df in 3.x
  df[df["A"] > 0]["B"] = 0
  df["B"][0] = 0

  # RIGHT — single .loc call on the object you want to change
  df.loc[df["A"] > 0, "B"] = 0
  df.loc[df.index[0], "B"] = 0
  ```
- `SettingWithCopyWarning` no longer exists. **Do not add defensive `.copy()`** calls to silence it — they only cost memory. Use `.copy()` only when you deliberately need an independent object for clarity.
- Avoid `inplace=True`; reassign instead (`df = df.dropna()`).

### 2.2 Dedicated string dtype ⚠️
- String columns are inferred as `str` (PyArrow-backed if installed), not `object`. `df.columns` is `Index(..., dtype='str')`.
- Do **not** test `df[col].dtype == object` to detect text. Use:
  ```python
  pd.api.types.is_string_dtype(df[col])
  ```
- A `str` column can hold only strings or missing values; assigning a non-string raises.
- Missing values in `str` columns are `NaN`; test with `pd.isna()`, never `is None` / `== np.nan`.

### 2.3 Datetime resolution
- Default resolution is now microseconds: `datetime64[us]` (was `ns`). Don't hard-code `datetime64[ns]` in dtype checks; use `pd.api.types.is_datetime64_any_dtype`.

### 2.4 Removed/renamed things — don't generate them
- `DataFrame.append` / `Series.append` → use `pd.concat`.
- `fillna(method="ffill")` → `ffill()` / `bfill()`.
- Uppercase / legacy frequency aliases (`"H"`, `"T"`, `"S"`, `"5Min"`) → use `"h"`, `"min"`, `"s"`, `"5min"`.
- `groupby(..., observed=...)` on categoricals now defaults to `observed=True`; pass `observed=False` explicitly if empty categories must appear.

---

## 3. Viewing & summarizing

```python
df.head(); df.tail(3)
df.index; df.columns; df.dtypes; df.shape
df.info()            # dtypes + non-null counts + memory
df.describe()        # numeric summary
df.T                 # transpose
df.sort_index(axis=1, ascending=False)
df.sort_values(by="B")
```

---

## 4. Selection

| Need | Use |
|---|---|
| Column(s) | `df["A"]`, `df[["B", "A"]]` |
| Rows + cols by **label** | `df.loc[rows, cols]` |
| Rows + cols by **position** | `df.iloc[rows, cols]` |
| Single scalar by label / position (fast) | `df.at[r, c]` / `df.iat[i, j]` |
| Boolean filter | `df[df["A"] > 0]`, `df.loc[mask, cols]` |
| Membership filter | `df[df["E"].isin(["two", "four"])]` |

Rules:
- **`.loc` slices are inclusive of both endpoints**; `.iloc` slices are end-exclusive (Python style).
- `df.A` attribute access only works for identifier-like names and may collide with methods (`df.count`, `df.T`). In generated code prefer `df["A"]`.
- Combine conditions with `&`, `|`, `~` and **parentheses**: `df[(df.A > 0) & (df.B < 1)]`. Never `and`/`or`.
- `df[df > 0]` masks non-matching cells to `NaN` (shape preserved).

### Setting values
```python
df["F"] = s1                         # aligned on index; non-matching labels → NaN
df.at[dates[0], "A"] = 0
df.iat[0, 1] = 0
df.loc[:, "D"] = np.array([5] * len(df))
df2[df2 > 0] = -df2                  # where-style set
df = df.assign(G=lambda d: d["A"] * 2)   # method-chain friendly
```

---

## 5. Missing data

- `np.nan` (NumPy dtypes), `pd.NA` (nullable dtypes), `NaT` (datetimes) all count as missing.
- Reductions **skip missing values by default** (`skipna=True`).

```python
df.isna() / pd.isna(df)
df.dropna(how="any")          # or how="all", subset=[...]
df.fillna(value=5)            # or a dict per column
df.ffill(); df.bfill()
df.reindex(index=..., columns=...)   # returns new object; new labels → NaN
```

Don't compare with `== np.nan` (always False).

---

## 6. Operations

- **Alignment:** binary ops between Series/DataFrames align on index/column labels (union); unmatched → `NaN`. This is a frequent source of silent NaNs — verify indexes or use `.to_numpy()` / `reset_index(drop=True)` deliberately.
  ```python
  df.sub(s, axis="index")
  ```
- Stats: `df.mean()` (per column), `df.mean(axis=1)` (per row).
- UDFs: `df.agg(func)` reduces, `df.transform(func)` returns same shape. Prefer built-in vectorized functions over `apply(lambda ...)` for speed.
- Counts: `s.value_counts()` (result Series named `"count"`).
- Strings: `s.str.lower()`, `.str.contains(...)`, `.str.replace(...)`; missing stays missing.

---

## 7. Combining data

```python
pd.concat([df_a, df_b, df_c])                    # row-wise
pd.concat([df_a, df_b], axis=1)                  # column-wise
pd.merge(left, right, on="key", how="inner")     # SQL-style join
```

- **Never build a DataFrame row-by-row in a loop** (each append copies). Collect a list of dicts/records, then `pd.DataFrame(records)` once.
- Duplicate keys on both sides produce a cartesian product per key. When the relationship should be 1:1 or many:1, guard it:
  ```python
  pd.merge(left, right, on="key", how="left", validate="many_to_one", indicator=True)
  ```
- After a merge, check row count and `_merge` value counts.

---

## 8. Grouping (split–apply–combine)

```python
df.groupby("A")[["C", "D"]].sum()
df.groupby(["A", "B"]).sum()                     # result has a MultiIndex
df.groupby("A").agg(total=("C", "sum"), n=("C", "size"))   # named aggregation
df.groupby("A", as_index=False)["C"].mean()      # flat result
df["C_share"] = df.groupby("A")["C"].transform(lambda x: x / x.sum())
```

- Select the value columns explicitly; don't rely on non-numeric columns being dropped.
- Categorical keys: pass `observed=False` to include empty categories.

---

## 9. Reshaping

```python
stacked = df2.stack()          # columns level → index level
stacked.unstack()              # inverse; unstacks LAST level by default
stacked.unstack(0)             # unstack a specific level
pd.pivot_table(df, values="D", index=["A", "B"], columns=["C"], aggfunc="mean")
df.melt(id_vars=[...])         # wide → long
```

- `pivot` fails on duplicate index/column pairs; use `pivot_table` with an `aggfunc`.
- Flatten a MultiIndex for export: `res.reset_index()`, or join column levels.

---

## 10. Time series

```python
rng = pd.date_range("2012-01-01", periods=100, freq="s")
ts = pd.Series(np.random.randint(0, 500, len(rng)), index=rng)
ts.resample("5min").sum()

ts_utc = ts.tz_localize("UTC")                 # naive → aware
ts_utc.tz_convert("Europe/Warsaw")             # aware → other zone
rng + pd.offsets.BusinessDay(5)
```

- Parse strings with `pd.to_datetime(col, format=...)` — give `format` when known (faster, unambiguous). Use `errors="coerce"` only intentionally.
- Use IANA zone names (`"Europe/Warsaw"`, `"America/New_York"`).
- `tz_localize` only on naive data; `tz_convert` only on aware data.
- `resample` requires a DatetimeIndex (or `on="col"`).

---

## 11. Categoricals

```python
df["grade"] = df["raw_grade"].astype("category")
df["grade"] = df["grade"].cat.rename_categories(["very good", "good", "very bad"])
df["grade"] = df["grade"].cat.set_categories(
    ["very bad", "bad", "medium", "good", "very good"])
df.sort_values("grade")                          # sorts by category order
df.groupby("grade", observed=False).size()       # includes empty categories
```

Use categoricals for low-cardinality string columns to save memory and impose an order.

---

## 12. Plotting

```python
import matplotlib.pyplot as plt
ax = df.plot()
plt.savefig("out.png", bbox_inches="tight")
plt.close("all")
```

Agents usually run headless: **save to file**, don't rely on `plt.show()`. Close figures to avoid memory growth.

---

## 13. I/O

```python
df.to_csv("out.csv", index=False)      # index=False unless the index is meaningful
pd.read_csv("in.csv")                  # consider dtype=, parse_dates=, usecols=, sep=, encoding=
df.to_parquet("out.parquet")           # needs pyarrow; preserves dtypes — preferred format
pd.read_parquet("in.parquet")
df.to_excel("out.xlsx", sheet_name="Sheet1", index=False)   # needs openpyxl
pd.read_excel("in.xlsx", sheet_name="Sheet1", na_values=["NA"])
```

- Writing CSV with the default `index=True` produces an `Unnamed: 0` column on re-read — a common bug.
- CSV loses dtypes; Parquet keeps them. Prefer Parquet for intermediate files.
- For European CSVs check `sep=";"`, `decimal=","`, `encoding` (e.g. `"cp1250"` for Polish Windows exports).
- Large files: `usecols=`, `dtype=`, `chunksize=`.

---

## 14. Gotchas checklist

- `if series:` → `ValueError: truth value ... is ambiguous`. Use `.empty`, `.any()`, `.all()`, `.item()`.
- `&`/`|` need parentheses around each condition.
- Chained assignment does nothing under CoW — use one `.loc[...] = ...`.
- Index alignment silently introduces `NaN`.
- Integer column with a missing value becomes `float64`; use nullable `"Int64"` if integers must stay integers.
- `df.loc[a:b]` includes `b`; `df.iloc[a:b]` excludes `b`.
- `merge` on non-unique keys multiplies rows.
- Don't detect strings via `dtype == object` in 3.x.
- Don't use removed APIs (`append`, `fillna(method=...)`, uppercase freq aliases).

---

## 15. Verification step (do this before reporting results)

After transforming data, the agent should confirm:
1. Row count is what's expected (especially after `merge`, `dropna`, filters).
2. `df.dtypes` match intent (no accidental `object`/`float` drift).
3. `df.isna().sum()` didn't grow unexpectedly (alignment/merge side effects).
4. Any numbers reported to the user were **computed by code**, not estimated.

---

### References
- 10 minutes to pandas: https://pandas.pydata.org/docs/user_guide/10min.html
- What's new in 3.0.0: https://pandas.pydata.org/docs/whatsnew/v3.0.0.html
- Copy-on-Write guide: https://pandas.pydata.org/docs/user_guide/copy_on_write.html
- String dtype migration (3.0): https://pandas.pydata.org/docs/user_guide/migration-3-strings.html