# Pandas Usage Guide for AI Agents

**Purpose:** Reference instructions for an LLM agent that needs to write or reason about pandas code. Based on the official "10 minutes to pandas" guide (pandas 3.0.x). Follow these conventions when generating pandas code so output is idiomatic, correct, and safe against common pitfalls.

---

## 0. Setup convention

Always import with the standard aliases:

```python
import numpy as np
import pandas as pd
```

## 1. Core objects

- **`Series`**: 1-D labeled array (any dtype).
- **`DataFrame`**: 2-D labeled table (rows + columns), the primary object you'll work with.

When creating a `DataFrame` from a dict of scalars/arrays, pandas infers a dtype **per column**, not one dtype for the whole table (unlike a raw NumPy array). Always check `df.dtypes` after construction if types matter downstream.

> **Note (pandas 3.0+):** plain Python strings now default to a dedicated `str` dtype rather than generic `object`. Don't assume `object` dtype for text columns — check `df.dtypes` rather than hardcoding assumptions.

## 2. Inspecting data — do this before transforming

Before writing any transformation logic, inspect the data:

- `df.head(n)` / `df.tail(n)` — peek at rows.
- `df.index`, `df.columns` — confirm labels/types.
- `df.dtypes` — confirm column types.
- `df.describe()` — quick numeric summary (count/mean/std/min/quartiles/max).
- `df.to_numpy()` — only when you need a raw array; note this may force a common dtype (often `object`) and is lossy for mixed-type frames — avoid it for typed pipelines.

## 3. Selecting data — use explicit accessors, not just `[]`

For interactive exploration, `[]`-based indexing is fine. **For production/generated code, prefer the explicit accessors** — they are less ambiguous and avoid `SettingWithCopyWarning` pitfalls:

| Need | Use |
|---|---|
| Single scalar, fast | `df.at[row_label, col_label]` / `df.iat[row_pos, col_pos]` |
| Rows/cols by label | `df.loc[...]` |
| Rows/cols by integer position | `df.iloc[...]` |
| Whole column(s) | `df["col"]` or `df[["col1", "col2"]]` |
| Row slice | `df[0:3]` (position) or `df["2013-01-02":"2013-01-04"]` (label) |

Rules the agent must remember:
- `df.loc` label slices are **inclusive of both endpoints**; `df.iloc` position slices are exclusive of the stop, like standard Python slicing.
- Attribute-style access (`df.A`) only works when the column name is a valid Python identifier with no conflicts with existing DataFrame methods — prefer `df["A"]` in generated code for robustness.
- Boolean masks (`df[df["A"] > 0]`, `df[df > 0]`) filter rows or elements; unmatched elements become `NaN`. Use `.isin([...])` for membership filters.

## 4. Setting values — avoid chained assignment

- Assigning a new column aligns on the index automatically: `df["new"] = some_series`.
- Use `.at[]` / `.iat[]` / `.loc[]` for setting single values or slices, e.g. `df.loc[:, "D"] = np.array([...])`.
- **Never chain indexers when assigning** (e.g. `df[df.A > 0]["B"] = 1`) — this is the classic `SettingWithCopyWarning` bug. Always assign through a single `.loc[...]` call instead.

## 5. Missing data

- Missing values are represented as `NaN` (for numeric/object-backed data); pandas excludes `NaN` from computations by default.
- `df.dropna(how="any")` — drop rows with any missing value.
- `df.fillna(value=x)` — fill missing values.
- `pd.isna(df)` — boolean mask of missing values.
- `df.reindex(index=..., columns=...)` returns a **copy** with a new index/column set — useful for introducing new columns before filling.

## 6. Operations & stats

- Aggregations (`df.mean()`, `.sum()`, `.std()`, etc.) exclude `NaN` by default and operate column-wise (`axis=0`) unless `axis=1` is passed for row-wise.
- Operations between two `Series`/`DataFrame` objects **align on index/columns first**, filling unmatched labels with `NaN` before computing.
- `df.agg(func)` — reduces each column to a scalar.
- `df.transform(func)` — applies a function elementwise/columnwise and returns a same-shaped result.
- `series.value_counts()` — frequency table of unique values.
- `series.str.<method>()` — vectorized string ops (`.lower()`, `.contains()`, `.replace()`, etc.) for text columns.

## 7. Combining data

- `pd.concat([df1, df2, ...])` — stack objects row-wise (or `axis=1` for column-wise). Prefer building a list of pieces and concatenating once, rather than appending in a loop (repeated appends are expensive since each row addition requires a copy).
- `pd.merge(left, right, on="key")` — SQL-style join. Specify `how="left"/"right"/"outer"/"inner"` explicitly rather than relying on the default (`inner`) when correctness matters.

## 8. Grouping (split–apply–combine)

```python
df.groupby("col_a")[["col_b", "col_c"]].sum()
df.groupby(["col_a", "col_b"]).sum()   # produces a MultiIndex result
```

Steps: split the data by key(s) → apply an aggregation/transformation to each group → combine into a result. For categorical group keys, pass `observed=False` explicitly if you want empty categories to appear in the result, or `observed=True` to suppress them (make this explicit — the default behavior differs by pandas version, don't rely on it implicitly).

## 9. Reshaping

- `df.stack()` — pivot the innermost column level into the row index (compress columns → rows).
- `df.unstack(level)` — inverse of `stack()`; default unstacks the last index level.
- `pd.pivot_table(df, values=..., index=..., columns=...)` — full pivot-table style reshape, supports aggregation for duplicate combinations.

## 10. Time series

- `pd.date_range(start, periods=n, freq=...)` — generate a `DatetimeIndex`.
- `series.resample("5min").sum()` — change frequency (e.g., downsample seconds → 5-minute buckets) with an aggregation.
- `series.tz_localize("UTC")` then `.tz_convert("US/Eastern")` — attach and convert time zones. Never do arithmetic mixing tz-naive and tz-aware timestamps.
- Adding calendar-aware offsets (e.g. `pd.offsets.BusinessDay(n)`) respects business-day semantics rather than naive fixed-duration addition.

## 11. Categorical data

- Convert with `df["col"] = df["col"].astype("category")`.
- Rename categories: `.cat.rename_categories([...])`.
- Reorder / add missing categories: `.cat.set_categories([...])`.
- Sorting a categorical column sorts by **category order**, not lexical order — call out this behavior if generating sort logic on categorical columns, since it can surprise users.

## 12. Plotting

- `series.plot()` / `df.plot()` uses matplotlib under the hood.
- In non-notebook environments, the agent must remind the user (or explicitly call) `plt.show()` to display, or `plt.savefig(path)` to persist to a file — a bare `.plot()` call produces no visible output in a plain script.

## 13. I/O

| Format | Write | Read |
|---|---|---|
| CSV | `df.to_csv(path)` | `pd.read_csv(path)` |
| Parquet | `df.to_parquet(path)` | `pd.read_parquet(path)` |
| Excel | `df.to_excel(path, sheet_name=...)` | `pd.read_excel(path, sheet_name, index_col=None, na_values=[...])` |

Default `to_csv` writes the index as an unnamed column on read-back (`Unnamed: 0`) unless `index=False` is passed on write or `index_col=0` is passed on read — the agent should set one of these explicitly whenever round-tripping data to avoid introducing a spurious column.

## 14. Known gotcha to guard against

Never use a `Series`/`DataFrame` directly in a boolean context (`if some_series:`) — pandas raises `ValueError: The truth value of a Series is ambiguous`. Use one of `.empty`, `.any()`, `.all()`, `.item()` (single-element case) depending on intent, and choose the one that matches the actual check being performed rather than defaulting to `.any()`.

---

## Summary checklist for the agent before emitting pandas code

1. Confirm dtypes are as expected (`.dtypes`) rather than assuming.
2. Prefer `.loc`/`.iloc`/`.at`/`.iat` over bare `[]` chaining for anything beyond quick exploration.
3. Never chain-assign into a filtered view.
4. Be explicit about `axis`, `how`, and `observed` parameters instead of relying on defaults.
5. Build lists of pieces and concatenate once instead of looping `.append`/repeated `concat`.
6. Set `index=False` on `to_csv` (or `index_col` on read) when round-tripping.
7. Never place a `Series`/`DataFrame` in a plain `if` condition.
