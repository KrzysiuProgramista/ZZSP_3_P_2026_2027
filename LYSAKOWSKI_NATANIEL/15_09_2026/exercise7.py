import pandas as pd

# --- Exercise 7 Part 1: Series Addition and NaN Explanation ---
print("====================== EXERCISE 7 PART 1 ==============")

# Create two Series with different indexes
s1 = pd.Series([5, 3], index=['a', 'b'])
s2 = pd.Series([10, 4], index=['a', 'c'])

print("\n--- Series s1 ---")
print(s1)
print("\n--- Series s2 ---")
print(s2)

# Addition using default behavior (where indices match, adds; where they don't, results in NaN)
s_sum = s1 + s2 
print("\n--- Sum (Default addition) ---")
print(s_sum)

# Addition using fill_value=0 (where indices don't match, fills with 0 instead of NaN)
s_sum_filled = s1.add(s2, fill_value=0)
print("\n--- Sum with add(fill_value=0) ---")
print(s_sum_filled)

# Why the difference? Default addition aligns on index AND performs element-wise operations. fill_value=0 forces the operation to proceed by substituting missing values with 0 instead of letting them propagate as NaN.

# Why Index Matters (Comment)
"""Index is what truly distinguishes Pandas from a basic list of lists; it provides labels that allow precise alignment, vectorized operations (like arithmetic addition or comparison), and powerful lookups beyond simple positional access."""


# --- Exercise 7 Part 2: The Weather Table (Murmansk) ---
print("\n\n====================== EXERCISE 7 PART 2: Weather Table ================")

# Data setup
weather = {
    "day":      ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "temp_c":   [-12, -15, -9, -3, 1, -2, -8],
    "wind_kmh": [22, 31, 18, 12, 9, 15, 27],
    "snow_cm":  [3, 8, 0, 0, 2, 5, 1],
}

# Build the DataFrame with 'day' as the index.
df_weather = pd.DataFrame(weather).set_index("day")

# Add columns
df_weather['feels_like'] = df_weather['temp_c'] - df_weather['wind_kmh'] / 5
df_weather['snowed'] = df_weather['snow_cm'] > 0

# Print required values
print("\n--- Analysis of Murmansk Weather ---")

# Coldest day (minimum temperature)
coldest_day = df_weather['temp_c'].idxmin()

# Windiest day (maximum wind)
windiest_day = df_weather['wind_kmh'].idxmax()

# Total snowfall
total_snowfall = df_weather['snow_cm'].sum()


print("\n--- Key Findings ---")
print(f"Coldest day: {coldest_day}")
print(f"Windiest day: {windiest_day}")
print(f"Total snowfall: {total_snowfall} cm")


# Filtered views
print("\n--- Days with Snow AND Temp < -5 ---")
snow_and_cold = df_weather[(df_weather['snowed']) & (df_weather['temp_c'] < -5)]
print(snow_and_cold)

# Averages based on conditions
avg_temp = df_weather.groupby('snowed')['temp_c'].mean()

print("\n--- Average Temperature by Snow Condition ---")
# Mapping True/False index back to readable status
condition_map = {"True": "Snowed", "False": "Did Not Snow"}
print(f"Average temp on snowy days: {avg_temp[True]}")
print(f"Average temp on non-snowy days: {avg_temp[False]}")