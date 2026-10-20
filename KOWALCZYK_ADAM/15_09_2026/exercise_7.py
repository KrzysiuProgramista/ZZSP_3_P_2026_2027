import numpy as np
import pandas as pd

# Two Series whose indexes only partially overlap: "b" and "c" are in both,
# "a" only in the left one, "d" only in the right one.
left  = pd.Series([1, 2, 3], index=["a", "b", "c"])
right = pd.Series([10, 20, 30], index=["b", "c", "d"])

print("left + right:")
print(left + right)
print()

# Why the NaNs:
# When two objects with different labels meet, the result is aligned to the *union*
# of the indexes — here ["a", "b", "c", "d"]. pandas matches values by LABEL, not by
# position, so "b" pairs with "b" and "c" with "c" no matter where they sit in each
# Series. For "a" and "d" there is nothing on the other side to add, and a missing
# operand makes the whole sum unknown -> np.nan. Note the dtype also goes int -> float,
# because np.nan is a float.

print("left.add(right, fill_value=0):")
print(left.add(right, fill_value=0))
print()

# The difference:
# `+` has no way to say what a missing operand should count as, so it gives up and
# writes NaN. `.add(other, fill_value=0)` substitutes 0 for whichever side is missing
# BEFORE adding, so "a" becomes 1 + 0 = 1 and "d" becomes 0 + 30 = 30. The index is
# still the union — fill_value changes the value, not the alignment. It only fills
# where exactly one side is missing; a label missing from both stays NaN.
# Pick the one that matches your intent: NaN means "unknown", 0 means "none recorded".

# Why the index is the thing that makes pandas different from a list of lists:
# A list of lists is addressed by POSITION — row 3, column 2 — so combining two of
# them means you are personally responsible for lining the rows up, and if one is
# sorted differently or is missing an entry, the code still runs and quietly returns
# wrong numbers. In pandas every value carries its LABEL, and every operation
# (arithmetic, assigning a column, merge, concat, groupby) aligns on that label first.
# The data can be in any order, of different lengths, and partially overlapping, and
# the result is still correct — with NaN marking the places that genuinely had no
# counterpart instead of a silent off-by-one. That is also why assigning a Series as a
# new column aligns on the index rather than on position: the label is the identity of
# the row, the position is just where it happens to be stored.


# used 0.1$

# after every prompt (exercise, i asked claude to add useful info
# to the md, so itll be more usefull next time and more token-friendly)