# Pandas / NumPy AI Rules

## <span style="color: red;">MUST</span>

- MUST use `pandas` for tabular data and `numpy` for numerical/array operations
- MUST use `DataFrame` as the main structure for tabular data.
- MUST use clear, logical, intuitive variable, alias and function names.
- MUST use descriptive column names, e.g. `Date`, `Location`, `Temperature`, `Notes`.
- MUST prefer pandas operations over manual Python loops.
- MUST use `.loc` for label/condition-based selection.
- MUST use `.iloc` for position-based selection.
- MUST use `.at` for single-value access by label.
- MUST use `.iat` for single-value access by position.
- MUST preserve meaningful indexes unless there is a reason to change them.

## <span style="color: gold;">SHOULD</span>

- SHOULD prefer simple, readable, vectorized operations.
- SHOULD use `.isin()` for membership filtering.
- SHOULD use `sort_values()` for sorting by column values.
- SHOULD use `sort_index()` for sorting by index.
- SHOULD use NumPy for numerical/array operations where appropriate.
- SHOULD use `.copy()` when creating a DataFrame that will be independently modified.
- SHOULD keep column names explicit instead of relying on column positions.

## <span style="color: red;">AVOID</span>

- AVOID unclear names such as `x`, `y`, `tmp`, `foo`, `data1`, `df2`.
- AVOID unnecessary row-by-row loops such as `iterrows()`.
- AVOID unnecessary DataFrame → NumPy → DataFrame conversions.
- AVOID chained indexing when modifying data.
- AVOID hard-coded column positions when column names are available.
- AVOID unnecessary one-liners that reduce readability.
- AVOID silently changing indexes, column names, or data types.
- AVOID using NumPy when a simpler pandas operation is clearer.

## <span style="color: darkgreen;">VERIFY</span>

- VERIFY the resulting DataFrame has the expected columns.
- VERIFY the number of rows after filtering, merging, or dropping data.
- VERIFY data types after conversions.
- VERIFY missing-value behavior.
- VERIFY that the index is preserved or intentionally changed.
- VERIFY that assignments modify the intended rows and columns.
- VERIFY that the final code is readable and logically consistent.
