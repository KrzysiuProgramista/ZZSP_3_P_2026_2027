import numpy as np
import pandas as pd

weather = {
    "day":      ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "temp_c":   [-12, -15, -9, -3, 1, -2, -8],
    "wind_kmh": [22, 31, 18, 12, 9, 15, 27],
    "snow_cm":  [3, 8, 0, 0, 2, 5, 1],
}

# set_index promotes "day" to the row index, so rows are labelled Mon..Sun
# instead of 0..6 — and idxmin/idxmax below then hand back the day name directly.
df = pd.DataFrame(weather).set_index("day")

# Element-wise arithmetic broadcasts across the whole column.
df["feels_like"] = df["temp_c"] - df["wind_kmh"] / 5

# A comparison returns a boolean Series.
df["snowed"] = df["snow_cm"] > 0

print(df)
print()

# idxmin/idxmax return the index LABEL of the extreme value — here the day name.
print("coldest day :", df["temp_c"].idxmin(), f'({df["temp_c"].min()} C)')
print("windiest day:", df["wind_kmh"].idxmax(), f'({df["wind_kmh"].max()} km/h)')
print("total snowfall:", df["snow_cm"].sum(), "cm")
print()

# Two boolean masks combined with & (bitwise, element-wise).
# The parentheses are required: & binds tighter than < in Python.
print("snowed AND below -5:")
print(df[(df["snowed"]) & (df["temp_c"] < -5)])
print()

# Average temperature split by whether it snowed.
# groupby on the boolean column: one group for False, one for True.
print("average temp by snowed:")
print(df.groupby("snowed")["temp_c"].mean())
print()

# The same thing written with masks, if you prefer it explicit:
print("avg temp, snowy days   :", df.loc[df["snowed"], "temp_c"].mean())
print("avg temp, snow-free days:", df.loc[~df["snowed"], "temp_c"].mean())

# used about 0.1$