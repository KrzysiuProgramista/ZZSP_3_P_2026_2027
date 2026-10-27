import pandas as pd
import numpy as np

# 1. Generowanie danych dla 20 fikcyjnych pracowników
np.random.seed(42)  # Stałe ziarno losowości dla powtarzalnych wyników

n_employees = 20
departments = ["IT", "HR", "Sales", "Finance"]

df = pd.DataFrame({
    "employee_id": range(1, n_employees + 1),
    "department": np.random.choice(departments, size=n_employees),
    "base_salary": np.random.randint(60_000, 160_000, size=n_employees),
    "years_worked": np.random.randint(0, 20, size=n_employees),
    "performance_score": np.random.randint(1, 6, size=n_employees) # Oceny od 1 do 5
})

# 2. Obliczenia wektoryzowane (kod ze slajdu)

# Dodatek stażowy: 2% za każdy rok pracy, ale maksymalnie 30% (0.30)
df["seniority_rate"] = (df["years_worked"] * 0.02).clip(upper=0.30)
df["seniority_bonus"] = df["base_salary"] * df["seniority_rate"]

# Premia za wyniki: mapowanie oceny (1-5) na odpowiedni procent
rate = df["performance_score"].map({1: 0, 2: 0, 3: 0.05, 4: 0.10, 5: 0.20})
df["performance_bonus"] = df["base_salary"] * rate

# Całkowite wynagrodzenie brutto (roczne)
df["total_salary"] = df["base_salary"] + df["seniority_bonus"] + df["performance_bonus"]

# Podatek progresywny (12% do 120 000 oraz 32% od nadwyżki powyżej 120 000)
df["tax"] = (
    0.12 * df["total_salary"].clip(upper=120_000) + 
    0.32 * (df["total_salary"] - 120_000).clip(lower=0)
)

# Wynagrodzenie netto
df["net_salary"] = df["total_salary"] - df["tax"]

# 3. Wyświetlenie wyników
print("--- Podgląd pierwszych 5 pracowników ---")
print(df.head().to_string(index=False))

print("\n--- Średnie wynagrodzenie netto według działu ---")
print(df.groupby("department")["net_salary"].mean().round(2))