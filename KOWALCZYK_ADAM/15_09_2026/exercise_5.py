import numpy as np
import pandas as pd

data = {
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
}
df_grades = pd.DataFrame(data)

# 1) Class average in maths.
print("class average in maths:", df_grades["maths"].mean())

# 2) Who scored highest in physics?
#    idxmax() returns the *index label* of the max value in a Series;
#    then .loc[label, "student"] pulls the name out of that row.
print("top in physics:", df_grades.loc[df_grades["physics"].idxmax(), "student"])

# 3) Each student's average across the three subjects (axis=1 -> across columns per row).
print("per-student average:")
print(df_grades[["maths", "physics", "english"]].mean(axis=1))

# 4) How many students scored 5 in english?
#    (s == 5) is a boolean Series; sum treats True as 1.
print("students with 5 in english:", (df_grades["english"] == 5).sum())

# 5) Average of all grades in the whole table.
#    Flatten the three numeric columns via to_numpy() and take a single mean.
print("overall grade average:", df_grades[["maths", "physics", "english"]].to_numpy().mean())


# used 0.19$

# after every prompt (exercise, i asked claude to add useful info
# to the md, so itll be more usefull next time and more token-friendly)