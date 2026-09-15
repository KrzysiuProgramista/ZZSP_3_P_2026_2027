# Exercise 5: A first real question**

# Using df_grades:
print(df_grades["maths"].mean())  # What is the class average in maths?

# Who scored highest in physics?
print(df_grades["physics"].idxmax())  # Output: 3 (the index of the row with the maximum value in the "physics" column)

# What is each student's average across the three subjects?
print(df_grades.groupby("student")[["maths", "physics", "english"]].mean())  # Output: a DataFrame with the average of each subject for each student

# How many students scored 5 in english?
print((df_grades["english"] == 5).sum())  # Output: 2 (the number of rows where the value in the "english" column is 5)

# What is the average of all grades in the whole table?
print(df_grades.mean().mean())  # Output: the mean of the mean of each column (i.e. the overall average)
