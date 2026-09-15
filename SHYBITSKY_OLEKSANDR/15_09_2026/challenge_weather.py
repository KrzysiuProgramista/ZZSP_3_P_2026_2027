"""Challenge: a week of weather in Murmansk."""

import pandas as pd

weather_data = {
    "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "temp_c": [-12, -15, -9, -3, 1, -2, -8],
    "wind_kmh": [22, 31, 18, 12, 9, 15, 27],
    "snow_cm": [3, 8, 0, 0, 2, 5, 1],
}

COLD_THRESHOLD_C = -5

# 1. The day names are the natural label of every row, so they become the index.
df_weather = pd.DataFrame(weather_data).set_index("day")
print("1. The weather table, indexed by day:")
print(df_weather)

# 2. A wind-chill style column: strong wind makes a cold day feel colder.
#    The whole column is computed in one vectorized expression, no loop.
df_weather["feels_like"] = df_weather["temp_c"] - df_weather["wind_kmh"] / 5

# 3. A boolean column: True on any day that recorded more than 0 cm of snow.
df_weather["snowed"] = df_weather["snow_cm"] > 0

print("\n2. + 3. With feels_like and snowed:")
print(df_weather)
print("\nColumn types:")
print(df_weather.dtypes)

# 4. The extremes of the week.
#    idxmin / idxmax return the INDEX LABEL, which here is the name of the day.
coldest_day = df_weather["temp_c"].idxmin()
windiest_day = df_weather["wind_kmh"].idxmax()
total_snowfall_cm = df_weather["snow_cm"].sum()
print("\n4. The week at a glance:")
print(f"coldest day:  {coldest_day} ({df_weather.at[coldest_day, 'temp_c']} C)")
print(f"windiest day: {windiest_day} ({df_weather.at[windiest_day, 'wind_kmh']} km/h)")
print(f"total snowfall: {total_snowfall_cm} cm")

# 5. Two conditions combined with & (and). Each condition is a boolean Series,
#    and each one needs its own brackets because & binds tighter than <.
cold_and_snowy = df_weather.loc[
    df_weather["snowed"] & (df_weather["temp_c"] < COLD_THRESHOLD_C)
]
print(f"\n5. Days with snow AND a temperature below {COLD_THRESHOLD_C} C:")
print(cold_and_snowy)
print("matching days:", list(cold_and_snowy.index), "->", len(cold_and_snowy), "of 7")

# 6. The same average, split by whether it snowed or not.
#    ~ is "not", so it flips the boolean column.
mean_temp_when_snowing = df_weather.loc[df_weather["snowed"], "temp_c"].mean()
mean_temp_when_dry = df_weather.loc[~df_weather["snowed"], "temp_c"].mean()
print("\n6. Average temperature, snowy days vs dry days:")
print(f"days it snowed:     {mean_temp_when_snowing:.2f} C")
print(f"days it did not:    {mean_temp_when_dry:.2f} C")

# groupby says the same thing in one expression, and shows how many days back each mean.
print("\nThe same split via groupby (False = dry days, True = snowy days):")
print(df_weather.groupby("snowed")["temp_c"].agg(["count", "mean"]))





# Cost of all exercises done at once: $1.37