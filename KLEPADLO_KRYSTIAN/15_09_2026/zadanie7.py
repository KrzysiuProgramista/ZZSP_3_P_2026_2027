# Exercise 7: Index matters
# Create two Series with different indexes and add them. Explain the NaNs.
# Use .add(other, fill_value=0) and explain the difference.
# Write in a comment why the index is the thing that makes pandas different
# from a list of lists.
#
# Challenge: The weather table
# Consider the following set of weather data for the city of Murmansk:
#
#     weather = {
#         "day":      ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
#         "temp_c":   [-12, -15, -9, -3, 1, -2, -8],
#         "wind_kmh": [22, 31, 18, 12, 9, 15, 27],
#         "snow_cm":  [3, 8, 0, 0, 2, 5, 1],
#     }
#
# Build the DataFrame with day as the index.
# Add a column feels_like = temp_c - wind_kmh / 5.
# Add a boolean column snowed.
# Print the coldest day, the windiest day and the total snowfall.
# Print only the days where it snowed AND the temperature was below -5.
# Print the average temperature on days it snowed, and on days it did not.
# Here's the code to complete Exercise 7 and the Challenge:

import pandas as pd

# Create two Series with different indexes and add them
s1 = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
s2 = pd.Series([4, 5, 6], index=[1, 2, 3])
print(s1.add(s2))  # Output: NaN where the indexes do not match

# Explain the NaNs: when adding two Series, the result is NaN where the indexes do not match.

# Use .add(other, fill_value=0) and explain the difference
print(s1.add(s2, fill_value=0))  # Output: 5 where the indexes do not match

print(df_weather['temp_c'][df_weather['snowed']].mean())  # Average temperature on days it snowed
print(df_weather['temp_c'][~df_weather['snowed']].mean())  # Average temperature on days it did not
