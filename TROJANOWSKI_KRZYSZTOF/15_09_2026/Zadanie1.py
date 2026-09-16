import numpy as np
import pandas as pd

# Exercise 1: Series
# Create a Series from a list of 6 numbers. Print it. Note the index.
s = pd.Series([1, 2, 3, 4, 5, 6])
print("Series with default index:", s)

# Create one with a custom string index.
s_custom_index = pd.Series([1, 2, 3, 4, 5, 6], index=['a', 'b', 'c', 'd', 'e', 'f'])
print("Series with custom string index:", s_custom_index)

# Create one from a dictionary - what becomes the index?
s_from_dict = pd.Series({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6})
print("Series from dictionary:", s_from_dict)

# Access an element by label and by position (s["a"] vs s.iloc[0]).
print("Accessing element by label 'a':", s_custom_index['a'])
print("Accessing element by position 0:", s_custom_index.iloc[0])

# Print s.values, s.index, s.dtype, s.name.
print("s.values:", s_custom_index.values)
print("s.index:", s_custom_index.index)
print("s.dtype:", s_custom_index.dtype)
print("s.name:", s_custom_index.name)

# Do arithmetic on the whole Series: s * 2, s + 10, s > 15.
print("s * 2:", s_custom_index * 2)
print("s + 10:", s_custom_index + 10)
print("s > 15:", s_custom_index > 15)
