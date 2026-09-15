# pandas — notes for the agent

Assume these two imports are already at the top of any snippet:

```python
import numpy as np
import pandas as pd
```

## The two objects

`Series` is a one-dimensional labeled array and it can hold anything — ints, strings,
arbitrary Python objects. `DataFrame` is the two-dimensional one: rows and columns, like
a table.

The thing worth remembering: a DataFrame keeps a dtype *per column*. A NumPy array has one
dtype for the whole array. This difference bites later, see `to_numpy()` below.

## Making them

```python
pd.Series([1, 3, 5, np.nan, 6, 8])          # no index given -> default RangeIndex
pd.Series([1, 2, 3], index=["a", "b", "c"]) # custom string index
pd.Series({"a": 1, "b": 2, "c": 3})         # from a dict — the keys become the index

dates = pd.date_range("20130101", periods=6)
pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))
```

From a dict, the keys become the column labels and the values become the columns. Scalars
get broadcast down the whole column:

```python
pd.DataFrame({
    "A": 1.0,
    "B": pd.Timestamp("20130102"),
    "C": pd.Series(1, index=range(4), dtype="float32"),
    "D": np.array([3] * 4, dtype="int32"),
    "E": pd.Categorical(["test", "train", "test", "train"]),
    "F": "foo",
})
```

You end up with a mix of dtypes here — `df.dtypes` shows what each column actually is.

The DataFrame constructor also accepts row-oriented input. Same shape, different layout:

```python
# list of dicts — one dict per row, keys become column labels,
# missing keys in any row become NaN in that column
pd.DataFrame([
    {"student": "Anna", "maths": 5},
    {"student": "Piotr", "maths": 3},
])

# list of lists — you have to pass columns=[...] because the rows carry no labels
pd.DataFrame(
    [["Anna", 5], ["Piotr", 3]],
    columns=["student", "maths"],
)
```

## Changing the index

`set_index("col")` promotes a column to be the row index and returns a new DataFrame.
`reset_index()` is the inverse — the current index moves back into a regular column and
the frame gets the default `RangeIndex` again.

```python
df2 = df.set_index("student")   # "student" is now the row label
df2.reset_index()               # back to numeric rows, "student" is a column again
```

Both return a new frame by default; pass `inplace=True` if you want to mutate. `set_index`
also accepts a list of columns for a MultiIndex.

## Series attributes and access

A Series has four attributes worth naming directly:

- `s.values` — the underlying array without the labels
- `s.index`  — the labels
- `s.dtype`  — singular. A Series is one column, so it has exactly one dtype (compare `df.dtypes`, which is per-column)
- `s.name`   — set via `pd.Series(..., name="grades")`, otherwise `None`. If the Series ends up as a column in a DataFrame, this becomes the column name.

Access is the same shape as for a DataFrame:

```python
s["a"]      # by label
s.iloc[0]   # by position
s.at["a"]   # scalar, fast
s.iat[0]    # scalar, fast, positional
```

Scalar and element-wise arithmetic broadcasts across the whole Series: `s * 2`, `s + 10`,
`s > 15` all return a Series aligned on the same index. The same works on a DataFrame.

## Looking at the data

`head()` and `tail(3)` for the top and bottom rows. `df.sample(n)` picks `n` random rows
(pass `random_state=...` for a reproducible pick). `df.shape` gives `(rows, cols)`.
`df.index` and `df.columns` are the labels, `df.dtypes` is the dtype of each column.
`df.T` transposes.

`df.info()` prints, in order:

1. the class of the object
2. the index type and the range of row labels
3. total column count
4. a per-column table with position, name, non-null count, and dtype
5. a dtype tally (how many columns of each dtype)
6. memory usage of the frame

`describe()` gives a quick statistical summary of the **numeric columns only** —
non-numeric columns are skipped. Its rows are:

- `count` — number of non-missing values
- `mean`  — arithmetic average
- `std`   — standard deviation (spread around the mean)
- `min`   — smallest value
- `25%` / `50%` / `75%` — quartiles; the 50% row is the median
- `max`   — largest value

Sorting comes in two flavours: `sort_index(axis=1, ascending=False)` sorts along an axis by
its labels, `sort_values(by="B")` sorts by the actual values.

`df.to_numpy()` gives you the underlying values without index or column labels. Careful
with it: pandas has to find a single NumPy dtype that fits every column, and if that ends up
being `object` the call copies the data. Fine on a homogeneous frame, wasteful on a mixed one.

## Selection

The docs are explicit about this, so treat it as a rule when writing production code: use
`loc`, `iloc`, `at` and `iat`. Plain `[]` and NumPy-style expressions are convenient when
poking around interactively, but they're not what you ship.

**With `[]`**

```python
df["A"]                     # one label -> the column as a Series
df.A                        # same thing; only works if the name is alnum + underscores
df[["B", "A"]]              # list of labels -> subset, in that order
df[0:3]                     # a slice selects rows, not columns
df["20130102":"20130104"]   # label slice, also rows
```

**By label — `loc` / `at`**

```python
df.loc[dates[0]]                          # a whole row
df.loc[:, ["A", "B"]]                     # all rows, two columns
df.loc["20130102":"20130104", ["A", "B"]] # label slices include both endpoints
df.loc[dates[0], "A"]                     # single value
df.at[dates[0], "A"]                      # same value, fast scalar access
```

Note the endpoint thing — label slicing is inclusive on both sides, integer slicing is not.
Easy to get wrong.

**By position — `iloc` / `iat`**

```python
df.iloc[3]               # fourth row
df.iloc[3:5, 0:2]        # behaves like NumPy / plain Python slicing
df.iloc[[1, 2, 4], [0, 2]]
df.iloc[1:3, :]          # rows only
df.iloc[:, 1:3]          # columns only
df.iloc[1, 1]            # a value
df.iat[1, 1]             # the same, fast path
```

**Boolean masks**

```python
df[df["A"] > 0]                       # keep matching rows
df[df > 0]                            # element-wise, non-matches become NaN
df2[df2["E"].isin(["two", "four"])]   # filter by membership
```

## Setting values

```python
df["F"] = s1                              # new column
df.at[dates[0], "A"] = 0                  # by label
df.iat[0, 1] = 0                          # by position
df.loc[:, "D"] = np.array([5] * len(df))  # from a NumPy array
df2[df2 > 0] = -df2                       # where-style conditional set
```

Assigning a Series as a new column aligns on the *index*, not on position. If the indexes
only partially overlap you get NaN in the gaps, which is usually the bug when someone says
"my column is half empty".

## Missing data

For NumPy dtypes, missing means `np.nan`, and computations leave it out by default.

`reindex(index=..., columns=...)` changes, adds or drops labels on an axis and hands back a
copy. Then `dropna(how="any")` throws out rows with anything missing, `fillna(value=5)`
substitutes, and `pd.isna(df)` gives you the boolean mask if you want to look before you act.

## Operations

`df.mean()` averages each column, `df.mean(axis=1)` each row. The other basic reductions
follow the same shape: `df.sum()`, `df.min()`, `df.max()`, `df.std()`, `df.median()`,
`df.count()`. They all work on a Series too (returning a scalar) and on a DataFrame
(returning a Series indexed by column).

`idxmax()` / `idxmin()` return the *index label* of the max/min instead of the value —
handy for "which row has the highest X" questions:

```python
df["physics"].idxmax()                 # index label of the top physics score
df.loc[df["physics"].idxmax(), "name"] # look up another column on that same row
```

Boolean masks double as counters, because `True` sums as 1 and `False` as 0:

```python
(df["english"] == 5).sum()   # how many rows equal 5
(df["maths"] > 3).mean()     # fraction of rows above 3
```

Reductions on a mixed frame fail when a column can't be reduced (e.g. strings and a
numeric mean in the same call). Pass `numeric_only=True` to skip non-numeric columns:

```python
df.mean(numeric_only=True)   # averages only int/float columns, ignores strings
```

When two objects with different labels meet, the result is aligned to the *union* of the
index or columns; pandas broadcasts along the dimension you specify and fills whatever
doesn't line up with `np.nan`. So `df.sub(s, axis="index")` will produce NaN rows wherever
`s` has nothing to offer.

For custom functions: `agg` when the function reduces, `transform` when it should come back
the same shape.

```python
df.agg(lambda x: np.mean(x) * 5.6)
df.transform(lambda x: x * 101.2)
```

Two more small ones: `s.value_counts()` for frequencies, and `s.str.<method>` for vectorized
string work — `s.str.lower()` and friends operate element-wise over the Series.

## Merging

`pd.concat([...])` glues objects together row-wise. `pd.merge(left, right, on="key")` does
SQL-style joins on a column. With duplicate keys on both sides you get every combination of
the matches; with unique keys it's the plain one-to-one join you'd expect.

A performance note from the docs that people ignore: adding a column is cheap, adding a
*row* requires a copy. Build a list of records first and pass it to the constructor rather
than appending in a loop.

## Grouping

Split the data into groups, apply something to each one, combine the results.

```python
df.groupby("A")[["C", "D"]].sum()
df.groupby(["A", "B"]).sum()     # grouping on several columns gives a MultiIndex
```

## Reshaping

`stack()` compresses a level of the columns into the index. `unstack()` is the inverse and
by default it works on the **last** level — pass a number to pick another one.

```python
index = pd.MultiIndex.from_arrays(arrays, names=["first", "second"])
stacked = df2.stack()
stacked.unstack()
stacked.unstack(1)
stacked.unstack(0)
```

Pivot tables take `values`, `index` and `columns`:

```python
pd.pivot_table(df, values="D", index=["A", "B"], columns=["C"])
```

## Time series

Resampling during frequency conversion is the headline feature here (think second-level data
into five-minute buckets — common in finance, not limited to it).

```python
rng = pd.date_range("1/1/2012", periods=100, freq="s")
ts.resample("5Min").sum()

ts.tz_localize("UTC")            # naive -> aware
ts_utc.tz_convert("US/Eastern")  # aware -> another zone
rng + pd.offsets.BusinessDay(5)  # adding a non-fixed duration
```

## Categoricals

```python
df["grade"] = df["raw_grade"].astype("category")
df["grade"] = df["grade"].cat.rename_categories(["very good", "good", "very bad"])
df["grade"] = df["grade"].cat.set_categories(
    ["very bad", "bad", "medium", "good", "very good"]
)
```

`set_categories` reorders and adds the missing ones in a single step. Methods under `.cat`
return a new Series by default, so assign the result back or nothing happens.

Once a column is categorical, `sort_values(by="grade")` follows the category order rather
than alphabetical order, and `df.groupby("grade", observed=False).size()` will show the
empty categories too.

## Plotting

Standard convention, `import matplotlib.pyplot as plt`. `ts.plot()` for a Series,
`df.plot()` draws every column. In Jupyter the figure shows up by itself; anywhere else you
need `plt.show()`, or `plt.savefig()` to write it out. `plt.close("all")` closes figures.

## Reading and writing

```python
df.to_csv("foo.csv")
pd.read_csv("foo.csv")

df.to_parquet("foo.parquet")
pd.read_parquet("foo.parquet")

df.to_excel("foo.xlsx", sheet_name="Sheet1")
pd.read_excel("foo.xlsx", "Sheet1", index_col=None, na_values=["NA"])
```

`to_csv` writes the index as a column, so a naive round-trip leaves you with a stray
`Unnamed: 0`. Parquet doesn't have that problem.

## One gotcha to memorize

```python
if pd.Series([False, True, False]):   # ValueError
```

The truth value of a Series is ambiguous. Use `.empty`, `.item()`, `.any()` or `.all()`
depending on what you actually meant.