import pandas as pd

# Build the DataFrame with day as the index
weather = {
    "day":      ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "temp_c":   [-12, -15, -9, -3, 1, -2, -8],
    "wind_kmh": [22, 31, 18, 12, 9, 15, 27],
    "snow_cm":  [3, 8, 0, 0, 2, 5, 1],
}
df_weather = pd.DataFrame(weather).set_index('day')

# Add a column feels_like = temp_c - wind_kmh / 5
df_weather['feels_like'] = df_weather['temp_c'] - df_weather['wind_kmh'] / 5

# Add a boolean column snowed
df_weather['snowed'] = df_weather['snow_cm'] > 0

# Print the coldest day, the windiest day and the total snowfall
print(df_weather.loc[df_weather['temp_c'].idxmin()])  # Coldest day
print(df_weather.loc[df_weather['wind_kmh'].idxmax()])  # Windiest day
print(df_weather['snow_cm'].sum())  # Total snowfall

# Print only the days where it snowed AND the temperature was below -5
print(df_weather[df_weather['snowed'] & (df_weather['temp_c'] < -5)])

# Print the average temperature on days it snowed, and on days it did not
print(df_weather['temp_c'][df_weather['snowed']].mean())  # Average temperature on days it snowed
print(df_weather['temp_c'][~df_weather['snowed']].mean())  # Average temperature on days it did not