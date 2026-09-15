"""Exercise 7: the index is what makes pandas different from lists of lists."""

import pandas as pd

# Two Series over overlapping, but not identical, labels.
morning_sales = pd.Series(
    {"bread": 10, "milk": 5, "eggs": 8, "butter": 2},
    name="morning_sales",
)
evening_sales = pd.Series(
    {"milk": 3, "eggs": 4, "cheese": 7},
    name="evening_sales",
)

print("morning_sales:")
print(morning_sales)
print("\nevening_sales:")
print(evening_sales)

# 1. Plain addition: pandas ALIGNS the two Series on their labels before adding.
total_sales = morning_sales + evening_sales
print("\n1. morning_sales + evening_sales:")
print(total_sales)
# Why the NaNs:
#   "milk" and "eggs" exist in both Series, so their values are really added (5+3, 8+4).
#   "bread" and "butter" only exist in the morning, "cheese" only in the evening.
#   For those labels one side has no value at all, and a number plus "nothing"
#   is not 0 - it is unknown, which pandas writes as NaN (Not a Number).
#   The result index is the UNION of both indexes, sorted, so all 5 products appear.
#   Note the dtype turned into float64: NaN cannot be stored in an int column.
print("\nlabels present in both:", sorted(set(morning_sales.index) & set(evening_sales.index)))
print("labels present in only one:", sorted(set(morning_sales.index) ^ set(evening_sales.index)))

# 2. The same addition, but a missing value is treated as 0.
total_sales_filled = morning_sales.add(evening_sales, fill_value=0)
print("\n2. morning_sales.add(evening_sales, fill_value=0):")
print(total_sales_filled)
# The difference:
#   "+" says "if either side is missing, the answer is unknown" -> NaN.
#   .add(..., fill_value=0) says "if ONE side is missing, pretend it sold 0 there",
#   so bread keeps its 10, butter its 2, cheese its 7, and nothing is lost.
#   fill_value only replaces a value that is missing on ONE side; a label missing
#   from BOTH Series would still be NaN, because there is nothing to fill in.

# 3. Why the index is the whole point.
# A list of lists is held together by POSITION: row 3 is "the fourth thing you
# appended", and nothing more. If you sort one list, filter another, or receive
# them in a different order, position 3 silently starts meaning something else and
# the mistake is invisible - the arithmetic still runs and still gives numbers.
# In pandas every value carries its LABEL with it. Operations align on those labels
# first, so "milk" is always added to "milk" no matter what order either side is in,
# and a label that is simply not there becomes a visible NaN instead of a silent
# wrong answer. The index is also what makes .loc, idxmax, set_index, joins and
# groupby possible: they all ask "which label?", never "which position?".
# That alignment-by-label is the difference between a table and a pile of lists.
reordered_evening_sales = evening_sales.sort_index()
print("\n3. The same evening data, now in alphabetical order:")
print(reordered_evening_sales)
print("\nAdded to the morning data, the result is identical -")
print("order never mattered, only the labels did:")
print(morning_sales.add(reordered_evening_sales, fill_value=0))
