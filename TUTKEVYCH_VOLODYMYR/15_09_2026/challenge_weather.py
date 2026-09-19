import numpy as np
import pandas as pd

weather = {
    "day":      ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "temp_c":   [-12, -15, -9, -3, 1, -2, -8],
    "wind_kmh": [22, 31, 18, 12, 9, 15, 27],
    "snow_cm":  [3, 8, 0, 0, 2, 5, 1],
}
df = pd.DataFrame(weather).set_index("day")

df["feels_like"] = df["temp_c"] - df["wind_kmh"] / 5
df["snowed"] = df["snow_cm"] > 0
print(df)

print("Coldest day:", df["temp_c"].idxmin())
print("Windiest day:", df["wind_kmh"].idxmax())
print("Total snowfall:", df["snow_cm"].sum())

print(df[df["snowed"] & (df["temp_c"] < -5)])

print(df.groupby("snowed")["temp_c"].mean())
