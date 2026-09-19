import numpy as np
import pandas as pd

df = pd.DataFrame({
    "student": ["Anna", "Piotr", "Ola", "Marek", "Kasia"],
    "maths":   [5, 3, 4, 2, 5],
    "physics": [4, 3, 5, 3, 4],
    "english": [5, 4, 4, 4, 5],
})
subjects = ["maths", "physics", "english"]

df["average"] = df[subjects].mean(axis=1)
df["passed"] = df["average"] >= 3.0
df["best_subject"] = df[subjects].idxmax(axis=1)  # przy remisie - pierwszy przedmiot

print(df.sort_values("average", ascending=False))
