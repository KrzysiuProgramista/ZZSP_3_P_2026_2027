import pandas as pd

df = pd.read_csv("employees.csv")

df["seniority_rate"] = (df["years_worked"] * 0.02).clip(upper=0.30)
df["seniority_bonus"] = df["base_salary"] * df["seniority_rate"]

rate = df["performance_score"].map({1: 0, 2: 0, 3: 0.05, 4: 0.10, 5: 0.20})
df["performance_bonus"] = df["base_salary"] * rate
df["total_salary"] = df["base_salary"] + df["seniority_bonus"] + df["performance_bonus"]

df["tax"] = 0.12 * df["total_salary"].clip(upper=120_000) + 0.32 * (
    df["total_salary"] - 120_000
).clip(lower=0)
df["net_salary"] = df["total_salary"] - df["tax"]

print(df.groupby("department")["net_salary"].mean().round(2))
