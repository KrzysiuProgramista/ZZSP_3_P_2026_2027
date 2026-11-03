import pandas as pd
import numpy as np

np.random.seed(42)

df = pd.DataFrame({
    "employee_id": range(1, 21),
    "name": [f"Employee {i}" for i in range(1, 21)],
    "department": np.random.choice(
        ["IT", "Sales", "HR", "Finance"], size=20
    ),
    "years_worked": np.random.randint(0, 21, size=20),
    "base_salary": np.random.randint(60000, 180001, size=20),
    "performance_score": np.random.randint(1, 6, size=20),
})

# 1. Seniority bonus: 2% per year worked, maximum 30%
df["seniority_rate"] = (df["years_worked"] * 0.02).clip(upper=0.30)
df["seniority_bonus"] = df["base_salary"] * df["seniority_rate"]

# 2. Performance bonus based on score
rate_map = {
    1: 0.00,
    2: 0.00,
    3: 0.05,
    4: 0.10,
    5: 0.20,
}
df["performance_bonus"] = (
    df["base_salary"] * df["performance_score"].map(rate_map)
)

# 3. Total salary
df["total_salary"] = (
    df["base_salary"]
    + df["seniority_bonus"]
    + df["performance_bonus"]
)

# 4. Progressive tax:
# 12% up to 120,000, then 32% only on the amount above 120,000
df["tax"] = (
    0.12 * df["total_salary"].clip(upper=120000)
    + 0.32 * (df["total_salary"] - 120000).clip(lower=0)
)

# 5. Net salary
df["net_salary"] = df["total_salary"] - df["tax"]

# 6. Average net salary by department
print(
    df.groupby("department")["net_salary"]
    .mean()
    .round(2)
)

print(df.head())