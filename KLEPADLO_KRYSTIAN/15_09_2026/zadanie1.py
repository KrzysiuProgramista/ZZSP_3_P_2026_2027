# Here's how you can accomplish the tasks you mentioned using pandas Series:

import pandas as pd
import numpy as np

# Create a Series from a list of 6 numbers
s = pd.Series([1, 2, 3, 4, 5, 6])
print("Series with default integer index:")
print(s)
print(s.index)

# Create one with a custom string index
s_custom_index = pd.Series([1, 2, 3, 4, 5, 6], index=['a', 'b', 'c', 'd', 'e', 'f'])
print("\nSeries with custom string index:")
print(s_custom_index)
print(s_custom_index.index)

# Create one from a dictionary
s_dict = pd.Series({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6})
print("\nSeries from dictionary:")
print(s_dict)
print(s_dict.index)

# Access an element by label and by position
print("\nAccess by label and position:")
print(s_dict["a"])  # Label
print(s_dict.iloc[0])  # Position

# Print s.values, s.index, s.dtype, s.name
print("\nSeries values, index, dtype, name:")
print(s_dict.values)
print(s_dict.index)
print(s_dict.dtype)
print(s_dict.name)

# Do arithmetic on the whole Series
print("\nArithmetic operations:")
print(s_dict * 2)
print(s_dict + 10)
print(s_dict > 15)

# Note: The last operation returns a boolean Series

# In this example, when you create a Series from a dictionary, the dictionary keys become the index of the Series.
# This is why `s_dict["a"]` and `s_dict.iloc[0]` both return the value associated with the key `'a'`.
