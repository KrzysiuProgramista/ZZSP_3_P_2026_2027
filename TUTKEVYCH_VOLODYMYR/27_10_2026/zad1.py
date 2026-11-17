import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 20
df = pd.DataFrame({
    "employee_id": [f"E{i:03d}" for i in range(1, n + 1)],
    "department": rng.choice(["Sales", "IT", "HR", "Finance"], n),
    "base_salary": rng.integers(60_000, 150_000, n),
    "years_worked": rng.integers(0, 25, n),
    "performance_score": rng.integers(1, 6, n),
})

# Надбавка за стаж: 2% за рік, але не більше 30%
df["seniority_rate"] = (df["years_worked"] * 0.02).clip(upper=0.30)
df["seniority_bonus"] = df["base_salary"] * df["seniority_rate"]

# Премія за результативність
perf_rate = df["performance_score"].map({1: 0, 2: 0, 3: 0.05, 4: 0.10, 5: 0.20})
df["performance_bonus"] = df["base_salary"] * perf_rate

df["total_salary"] = df["base_salary"] + df["seniority_bonus"] + df["performance_bonus"]

# Податок: 12% до 120 000, 32% з перевищення
df["tax"] = (0.12 * df["total_salary"].clip(upper=120_000)
             + 0.32 * (df["total_salary"] - 120_000).clip(lower=0))
df["net_salary"] = df["total_salary"] - df["tax"]

print(df.groupby("department")["net_salary"].mean().round(2))