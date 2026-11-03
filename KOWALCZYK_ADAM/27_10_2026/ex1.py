import numpy as np
import pandas as pd

INPUT_CSV = "employees.csv"
OUTPUT_CSV = "salaries.csv"

TAX_THRESHOLD = 120_000
LOWER_RATE = 0.12
UPPER_RATE = 0.32

SENIORITY_PER_YEAR = 0.02
SENIORITY_CAP = 0.30

PERFORMANCE_RATES = {1: 0.00, 2: 0.00, 3: 0.05, 4: 0.10, 5: 0.20}

OUTPUT_COLUMNS = [
    "first_name", "last_name", "department", "years_worked", "base_salary",
    "performance_score", "seniority_rate", "seniority_bonus",
    "performance_bonus", "total_salary", "tax", "net_salary",
]


def add_salary_columns(df):
    out = df.copy()

    out["seniority_rate"] = (
        out["years_worked"] * SENIORITY_PER_YEAR
    ).clip(upper=SENIORITY_CAP)
    out["seniority_bonus"] = out["base_salary"] * out["seniority_rate"]

    performance_rate = out["performance_score"].map(PERFORMANCE_RATES)
    if performance_rate.isna().any():
        unknown = out.loc[performance_rate.isna(), "performance_score"].unique()
        raise ValueError(f"unknown performance_score values: {unknown}")
    out["performance_bonus"] = out["base_salary"] * performance_rate

    out["total_salary"] = (
        out["base_salary"] + out["seniority_bonus"] + out["performance_bonus"]
    )

    out["tax"] = (
        LOWER_RATE * out["total_salary"].clip(upper=TAX_THRESHOLD)
        + UPPER_RATE * (out["total_salary"] - TAX_THRESHOLD).clip(lower=0)
    )
    out["net_salary"] = out["total_salary"] - out["tax"]

    money = ["seniority_bonus", "performance_bonus", "total_salary",
             "tax", "net_salary"]
    out[money] = out[money].round(2)
    return out[OUTPUT_COLUMNS]


def main():
    raw = pd.read_csv(INPUT_CSV)
    before = raw.copy(deep=True)

    salaries = add_salary_columns(raw)

    pd.testing.assert_frame_equal(raw, before)

    assert np.allclose(salaries["net_salary"] + salaries["tax"],
                       salaries["total_salary"], atol=0.01)
    assert (salaries["seniority_rate"] <= SENIORITY_CAP).all()

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)

    print(f"{len(salaries)} employees loaded from {INPUT_CSV}\n")
    print("--- full table ---")
    print(salaries.to_string(index=False))

    print("\n--- average net_salary per department ---")
    print(salaries.groupby("department")["net_salary"].mean().round(2))

    print("\n--- who hit the seniority cap (30%)? ---")
    capped = salaries.loc[salaries["seniority_rate"] >= SENIORITY_CAP]
    print(capped[["first_name", "last_name", "years_worked",
                  "seniority_rate"]].to_string(index=False))

    print("\n--- who pays the 32% rate on part of their salary? ---")
    upper = salaries.loc[salaries["total_salary"] > TAX_THRESHOLD]
    print(f"{len(upper)} of {len(salaries)} employees "
          f"(total_salary above {TAX_THRESHOLD:,})")

    print("\n--- effective tax rate ---")
    effective = (salaries["tax"] / salaries["total_salary"] * 100).round(2)
    print(f"min {effective.min()}%  mean {effective.mean().round(2)}%  "
          f"max {effective.max()}%")

    salaries.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWritten: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()