# Pandas Agent Instructions

Reference notes for an AI coding agent working with the `pandas` library (based on pandas 3.0.5, "10 minutes to pandas"). Use these as quick rules-of-thumb before writing pandas code.

## Setup

```python
import numpy as np
import pandas as pd
```

## Core objects

- `Series`: 1D labeled array (like a single column).
- `DataFrame`: 2D labeled table (rows + columns), the main object you'll usually work with.

## Creating data

```python
s = pd.Series([1, 3, 5, np.nan, 6, 8])                     # Series from a list
dates = pd.date_range("20130101", periods=6)                # DatetimeIndex
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))
df2 = pd.DataFrame({"A": 1.0, "B": pd.Timestamp("20130102"), "C": "foo"})  # from a dict
```

- Column dtypes can differ per column: check with `df.dtypes`.

## Viewing data

- `df.head(n)` / `df.tail(n)`: first/last n rows.
- `df.index`, `df.columns`: labels.
- `df.to_numpy()`: strip labels, get raw NumPy array (single dtype: pandas upcasts if columns differ).
- `df.describe()`: quick stats summary (count, mean, std, min, quartiles, max).
- `df.T`: transpose.
- `df.sort_index(axis=1, ascending=False)`: sort by axis labels.
- `df.sort_values(by="col")`: sort by column values.

## Selection: pick the right tool

**Rule of thumb: prefer `.loc` (labels) and `.iloc` (integer position) over bare `[]` in production code.**

| Goal | Syntax |
|---|---|
| Select column | `df["A"]` or `df.A` |
| Select multiple columns | `df[["B", "A"]]` |
| Slice rows by position | `df[0:3]` |
| Slice rows by label | `df["20130102":"20130104"]` |
| Row by label | `df.loc[dates[0]]` |
| Rows+cols by label | `df.loc[:, ["A", "B"]]` (label slices are **inclusive** on both ends) |
| Single scalar by label (fast) | `df.at[dates[0], "A"]` |
| Row by position | `df.iloc[3]` |
| Rows+cols by position | `df.iloc[3:5, 0:2]` |
| Single scalar by position (fast) | `df.iat[1, 1]` |
| Boolean filter | `df[df["A"] > 0]` |
| Filter by membership | `df[df["E"].isin(["two", "four"])]` |

## Setting values

```python
df["F"] = s1                     # new column, aligned by index
df.at[dates[0], "A"] = 0         # set by label
df.iat[0, 1] = 0                 # set by position
df.loc[:, "D"] = np.array([5] * len(df))
df[df > 0] = -df                 # conditional set (where-style)
```

## Missing data

- Missing values are `np.nan`; excluded from computations by default.
- `df.reindex(index=..., columns=...)`: reshape/add labels (returns a copy).
- `df.dropna(how="any")`: drop rows with any NaN.
- `df.fillna(value=5)`: fill NaN.
- `pd.isna(df)`: boolean mask of NaNs.

## Operations

- `df.mean()`: column means; `df.mean(axis=1)`: row means.
- Ops between objects align on the union of index/columns, filling gaps with NaN.
- `df.agg(func)`: reduce with a custom function.
- `df.transform(func)`: broadcast a custom function (same shape out).
- `s.value_counts()`: frequency counts.
- `s.str.lower()` etc.: vectorized string ops via `.str` accessor.

## Combining data

- `pd.concat([df1, df2, ...])`: stack row-wise. Prefer building a full list of pieces/records over appending row-by-row (row appends are expensive; column adds are cheap).
- `pd.merge(left, right, on="key")`: SQL-style join.

## Grouping (split-apply-combine)

```python
df.groupby("A")[["C", "D"]].sum()
df.groupby(["A", "B"]).sum()        # multiple keys -> MultiIndex result
```

## Reshaping

- `df.stack()`: pivot columns into a row level (compress columns into MultiIndex rows).
- `stacked.unstack()`: inverse of stack (default: last level).
- `pd.pivot_table(df, values="D", index=["A", "B"], columns=["C"])`: spreadsheet-style pivot.

## Time series

- `pd.date_range(start, periods=..., freq=...)`: build a date index.
- `series.resample("5Min").sum()`: change frequency (e.g., downsample).
- `series.tz_localize("UTC")`: attach a timezone.
- `series.tz_convert("US/Eastern")`: convert timezone.
- `rng + pd.offsets.BusinessDay(5)`: calendar-aware date arithmetic.

## Categorical data

```python
df["grade"] = df["raw_grade"].astype("category")
df["grade"] = df["grade"].cat.rename_categories(["very good", "good", "very bad"])
df["grade"] = df["grade"].cat.set_categories(["very bad", "bad", "medium", "good", "very good"])
df.sort_values(by="grade")                       # sorts by category order, not lexical
df.groupby("grade", observed=False).size()        # observed=False keeps empty categories
```

## Plotting

```python
import matplotlib.pyplot as plt
df.plot()
plt.show()   # or plt.savefig("out.png") outside Jupyter
```

## I/O

| Format | Write | Read |
|---|---|---|
| CSV | `df.to_csv("foo.csv")` | `pd.read_csv("foo.csv")` |
| Parquet | `df.to_parquet("foo.parquet")` | `pd.read_parquet("foo.parquet")` |
| Excel | `df.to_excel("foo.xlsx", sheet_name="Sheet1")` | `pd.read_excel("foo.xlsx", "Sheet1")` |

## Gotchas to avoid

- **Never** use a `Series`/`DataFrame` directly in an `if` statement: truth value is ambiguous. Use `.empty`, `.any()`, `.all()`, or `.item()` instead.
- Bare `[]` slicing mixes label/position semantics depending on input type: use `.loc`/`.iloc` to be explicit and avoid bugs.
- `.to_numpy()` on mixed-dtype frames upcasts to `object` and requires a copy: expect a performance hit.

## Agent checklist before writing pandas code

1. Confirm whether row-position or label-based indexing is needed: pick `.iloc` or `.loc` explicitly.
2. Avoid iterative row appends; build a list of dicts/rows and construct the DataFrame once.
3. Check for NaNs before aggregating if the result must not silently drop data.
4. When filtering with boolean masks, confirm the mask's index aligns with the DataFrame's index.
5. Prefer vectorized `.str`/`.dt` accessor methods over Python loops for per-element ops.

Source: [pandas: 10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
