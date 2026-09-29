# Pandas Instructions for AI LLM Agents

## Overview

This document provides essential pandas patterns and operations for AI agents working with tabular data in Python. Based on the official "10 minutes to pandas" guide, these are the core operations you'll need most frequently. 

## Standard Import Pattern

Always start with these imports:

```python
import numpy as np
import pandas as pd
```

## Core Data Structures

### Series (1D)
A one-dimensional labeled array that can hold any data type (integers, strings, floats, Python objects). 

```python
s = pd.Series([1, 3, 5, np.nan, 6, 8])
```

### DataFrame (2D)
A two-dimensional labeled data structure with columns of potentially different types—think of it as a spreadsheet or SQL table. 

```python
# From NumPy array with datetime index
dates = pd.date_range("20130101", periods=6)
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))

# From dictionary
df2 = pd.DataFrame({
    "A": 1.0,
    "B": pd.Timestamp("20130102"),
    "C": pd.Series(1, index=list(range(4)), dtype="float32"),
    "D": np.array([3] * 4, dtype="int32"),
    "E": pd.Categorical(["test", "train", "test", "train"]),
    "F": "foo"
})
```

## Viewing Data

| Operation | Code | Description |
|-----------|------|-------------|
| First rows | `df.head()` | View top 5 rows |
| Last rows | `df.tail(3)` | View last 3 rows |
| Index | `df.index` | Show row labels |
| Columns | `df.columns` | Show column names |
| Underlying data | `df.to_numpy()` | Get NumPy array (no labels) |
| Summary stats | `df.describe()` | Quick statistical summary |
| Transpose | `df.T` | Swap rows and columns |
| Sort by index | `df.sort_index(axis=1, ascending=False)` | Sort columns |
| Sort by values | `df.sort_values(by="B")` | Sort by column B |

## Selection Methods

### GetItem (`[]`)

```python
# Single column (returns Series)
df["A"]
df.A  # Alternative if column name is simple

# Multiple columns
df[["B", "A"]]

# Row slicing
df[0:3]
df["20130102":"20130104"]  # Date slicing
```

### Selection by Label (`loc`)

Use `loc` for label-based indexing. Both endpoints are **included** in slices. 

```python
# Single row
df.loc[dates[0]]

# All rows, specific columns
df.loc[:, ["A", "B"]]

# Row and column slicing (inclusive)
df.loc["20130102":"20130104", ["A", "B"]]

# Single value
df.loc[dates[0], "A"]

# Fast scalar access
df.at[dates[0], "A"]
```

### Selection by Position (`iloc`)

Use `iloc` for integer position-based indexing (NumPy-style). 

```python
# Single row by position
df.iloc[3]

# Row and column slices
df.iloc[3:5, 0:2]

# Specific positions
df.iloc[[1, 2, 4], [0, 2]]

# Fast scalar access
df.iat[1, 1]
```

### Boolean Indexing

```python
# Rows where column A > 0
df[df["A"] > 0]

# Values where condition is met (others become NaN)
df[df > 0]

# Using isin() for filtering
df2[df2["E"].isin(["two", "four"])]
```

## Setting Values

```python
# Add new column (auto-aligns by index)
df["F"] = s1

# Set by label
df.at[dates[0], "A"] = 0

# Set by position
df.iat[0, 1] = 0

# Set entire column with array
df.loc[:, "D"] = np.array([5] * len(df))

# Conditional setting
df2[df2 > 0] = -df2
```

## Missing Data Handling

pandas uses `np.nan` for missing data. It's excluded from computations by default. 

```python
# Drop rows with any missing data
df1.dropna(how="any")

# Fill missing values
df1.fillna(value=5)

# Get boolean mask of missing values
pd.isna(df1)
```

## Operations

### Statistics

```python
# Mean per column
df.mean()

# Mean per row
df.mean(axis=1)

# Custom aggregation
df.agg(lambda x: np.mean(x) * 5.6)

# Custom transformation
df.transform(lambda x: x * 101.2)
```

### Value Counts

```python
s = pd.Series(np.random.randint(0, 7, size=10))
s.value_counts()
```

### String Methods

Access string methods via the `str` attribute: 

```python
s = pd.Series(["A", "B", "C", "Aaba", "Baca", np.nan, "CABA", "dog", "cat"])
s.str.lower()
```

## Merging Data

### Concatenation

```python
# Split and recombine
pieces = [df[:3], df[3:7], df[7:]]
pd.concat(pieces)
```

**Important:** Adding columns is fast; adding rows iteratively is slow. Build DataFrames from pre-built lists when possible. 

### Join/Merge

SQL-style joins on specific columns: 

```python
left = pd.DataFrame({"key": ["foo", "foo"], "lval": [1, 2]})
right = pd.DataFrame({"key": ["foo", "foo"], "rval": [4, 5]})
pd.merge(left, right, on="key")
```

## Grouping

GroupBy follows split-apply-combine pattern: 

```python
df = pd.DataFrame({
    "A": ["foo", "bar", "foo", "bar", "foo", "bar", "foo", "foo"],
    "B": ["one", "one", "two", "three", "two", "two", "one", "three"],
    "C": np.random.randn(8),
    "D": np.random.randn(8),
})

# Group by single column
df.groupby("A")[["C", "D"]].sum()

# Group by multiple columns (MultiIndex)
df.groupby(["A", "B"]).sum()
```

## Reshaping

### Stack/Unstack

```python
# Stack: compress column level into index
stacked = df2.stack()

# Unstack: expand index level back to columns
stacked.unstack()
stacked.unstack(1)  # Unstack specific level
```

### Pivot Tables

```python
pd.pivot_table(df, values="D", index=["A", "B"], columns=["C"])
```

## Time Series

```python
# Create time range
rng = pd.date_range("1/1/2012", periods=100, freq="s")
ts = pd.Series(np.random.randint(0, 500, len(rng)), index=rng)

# Resample (e.g., seconds to 5-minute bins)
ts.resample("5Min").sum()

# Timezone operations
ts_utc = ts.tz_localize("UTC")  # Localize to UTC
ts_utc.tz_convert("US/Eastern")  # Convert to Eastern

# Add business days
rng + pd.offsets.BusinessDay(5)
```

## Categorical Data

```python
# Convert to categorical
df["grade"] = df["raw_grade"].astype("category")

# Rename categories
df["grade"] = df["grade"].cat.rename_categories(["very good", "good", "very bad"])

# Reorder and add missing categories
df["grade"] = df["grade"].cat.set_categories(
    ["very bad", "bad", "medium", "good", "very good"]
)

# Sort by category order (not alphabetical)
df.sort_values(by="grade")

# GroupBy shows empty categories with observed=False
df.groupby("grade", observed=False).size()
```

## Import/Export

### CSV

```python
# Write
df.to_csv("foo.csv")

# Read
pd.read_csv("foo.csv")
```

### Parquet

```python
# Write
df.to_parquet("foo.parquet")

# Read
pd.read_parquet("foo.parquet")
```

### Excel

```python
# Write
df.to_excel("foo.xlsx", sheet_name="Sheet1")

# Read
pd.read_excel("foo.xlsx", "Sheet1", index_col=None, na_values=["NA"])
```

## Common Gotchas

### Boolean Truth Value Ambiguity

Never use a Series or DataFrame directly in an `if` statement: 

```python
# WRONG - raises ValueError
if pd.Series([False, True, False]):
    print("I was true")

# RIGHT - use .any(), .all(), .empty, or .bool()
if pd.Series([False, True, False]).any():
    print("At least one is true")
```

## Quick Reference: When to Use What

| Task | Method | Notes |
|------|--------|-------|
| Select column | `df["col"]` or `df.col` | Returns Series |
| Select by label | `df.loc[row, col]` | Inclusive slicing |
| Select by position | `df.iloc[row_idx, col_idx]` | NumPy-style |
| Fast scalar get | `df.at[row, col]` | Faster than `loc` |
| Fast scalar set | `df.iat[row_idx, col_idx]` | Faster than `iloc` |
| Filter rows | `df[df["col"] > 0]` | Boolean indexing |
| Handle missing | `dropna()`, `fillna()` | `np.nan` is default |
| Group data | `df.groupby("col")` | Split-apply-combine |
| Reshape | `stack()`, `unstack()`, `pivot_table()` | Restructure data |
| Time operations | `resample()`, `tz_localize()` | Frequency conversion |

