"""Exercise 1: Series - the one-dimensional pandas structure."""

import pandas as pd

# 1. A Series built from a plain list of 6 numbers.
#    No index was given, so pandas creates a default RangeIndex: 0, 1, 2, 3, 4, 5.
temperatures = pd.Series([12, 18, 25, 7, 30, 21])
print("1. Series from a list (default RangeIndex 0..5):")
print(temperatures)

# 2. The same values, but with our own string index (labels instead of positions).
labelled_temperatures = pd.Series(
    [12, 18, 25, 7, 30, 21],
    index=["a", "b", "c", "d", "e", "f"],
)
print("\n2. Series with a custom string index:")
print(labelled_temperatures)

# 3. A Series from a dictionary.
#    The dictionary KEYS become the index, the dictionary VALUES become the data.
city_populations = {
    "Warsaw": 1_860_000,
    "Krakow": 800_000,
    "Gdansk": 486_000,
    "Poznan": 541_000,
}
population_series = pd.Series(city_populations)
print("\n3. Series from a dictionary (the keys became the index):")
print(population_series)
print("index built from the dict keys:", list(population_series.index))

# 4. Two different ways of reaching an element.
#    - by LABEL  -> the name stored in the index
#    - by POSITION -> where the value physically sits, counting from 0
print("\n4. Access by label vs by position:")
print('labelled_temperatures["a"]   (by label)    ->', labelled_temperatures["a"])
print("labelled_temperatures.iloc[0] (by position) ->", labelled_temperatures.iloc[0])
print('labelled_temperatures.loc["c"] (by label)   ->', labelled_temperatures.loc["c"])
print("labelled_temperatures.iloc[2] (by position) ->", labelled_temperatures.iloc[2])
# Here both ways point to the same element, but that is a coincidence of this index.
# Sort or filter the Series and the label keeps following its value, the position does not.

# 5. The attributes that describe a Series.
named_temperatures = pd.Series(
    [12, 18, 25, 7, 30, 21],
    index=["a", "b", "c", "d", "e", "f"],
    name="temperature_c",
)
print("\n5. Series attributes:")
print("values (the raw data as a NumPy array):", named_temperatures.values)
print("index  (the labels):", named_temperatures.index)
print("dtype  (the type of the values):", named_temperatures.dtype)
print("name   (the name of the Series):", named_temperatures.name)

# 6. Arithmetic works on the WHOLE Series at once (vectorized, no loop needed).
#    The index is carried along untouched; only the values change.
print("\n6. Whole-Series arithmetic:")
print("named_temperatures * 2:")
print(named_temperatures * 2)
print("\nnamed_temperatures + 10:")
print(named_temperatures + 10)
print("\nnamed_temperatures > 15  (a boolean Series - the basis of every pandas filter):")
print(named_temperatures > 15)
print("\nUsing that boolean Series to select rows with .loc:")
print(named_temperatures.loc[named_temperatures > 15])
