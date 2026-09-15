# Exercise 4: Inspecting**

# Using df_grades:
print(df_grades.head(2))  # Print the first 2 rows
print(df_grades.tail(2))  # Print the last 2 rows
print(df_grades.sample(3))  # Print 3 random rows

# df["maths"] is a Series
print(type(df_grades["maths"]))  # Output: <class 'pandas.core.series.Series'>

# df[["maths", "physics"]] is a DataFrame
print(type(df_grades[["maths", "physics"]]))  # Output: <class 'pandas.core.frame.DataFrame'>

# The difference is that df["maths"] is a Series (one column) and df[["maths", "physics"]] is a DataFrame (multiple columns)

# df["maths"] is a Series
print(df_grades["maths"].mean())  # Print the mean of the "maths" column
print(df_grades["maths"].max())  # Print the maximum of the "maths" column
print(df_grades["maths"].min())  # Print the minimum of the "maths" column
print(df_grades["maths"].sum())  # Print the sum of the "maths" column
print(df_grades["maths"].std())  # Print the standard deviation of the "maths" column

# df.mean(numeric_only=True) is the mean of every column at once
print(df_grades.mean(numeric_only=True))
