"""Challenge 1: salary calculator (20 fictional employees, vectorised operations)."""
import pandas as pd


def calculate_salaries(df: pd.DataFrame) -> pd.DataFrame:
    """Return a new DataFrame with annual bonuses, progressive tax and net salary."""
    result = df.copy()
    result["seniority_rate"] = (result["years_worked"] * 0.02).clip(upper=0.30)
    result["seniority_bonus"] = result["base_salary"] * result["seniority_rate"]
    score_rates = {1: 0.00, 2: 0.00, 3: 0.05, 4: 0.10, 5: 0.20}
    rates = result["performance_score"].map(score_rates)
    if rates.isna().any():
        raise ValueError("performance_score must be from 1 to 5")
    result["performance_bonus"] = result["base_salary"] * rates
    result["total_salary"] = (
        result["base_salary"] + result["seniority_bonus"] + result["performance_bonus"]
    )
    result["tax"] = (
        0.12 * result["total_salary"].clip(upper=120_000)
        + 0.32 * (result["total_salary"] - 120_000).clip(lower=0)
    )
    result["net_salary"] = result["total_salary"] - result["tax"]
    return result


if __name__ == "__main__":
    # Fictional example data: annual gross base_salary in PLN.
    people = [
        (1, "Anna", "Nowak", "IT", 4, 5, 100000),
        (2, "Piotr", "Kowalski", "HR", 2, 3, 65000),
        (3, "Maria", "Wiśniewska", "Sales", 8, 4, 90000),
        (4, "Jan", "Zieliński", "Finance", 15, 5, 130000),
        (5, "Ola", "Wójcik", "IT", 1, 2, 78000),
        (6, "Kamil", "Kamiński", "Sales", 5, 3, 72000),
        (7, "Zofia", "Lewandowska", "HR", 11, 4, 85000),
        (8, "Tomasz", "Dąbrowski", "Finance", 7, 2, 115000),
        (9, "Natalia", "Kozłowska", "IT", 18, 5, 150000),
        (10, "Michał", "Jankowski", "Sales", 3, 1, 55000),
        (11, "Julia", "Mazur", "Finance", 9, 3, 98000),
        (12, "Paweł", "Krawczyk", "HR", 6, 5, 73000),
        (13, "Karolina", "Piotrowska", "IT", 12, 4, 120000),
        (14, "Adam", "Grabowski", "Sales", 0, 2, 52000),
        (15, "Emilia", "Pawlak", "Finance", 20, 4, 145000),
        (16, "Filip", "Michalski", "HR", 4, 3, 61000),
        (17, "Weronika", "Król", "IT", 6, 5, 107000),
        (18, "Bartosz", "Wieczorek", "Sales", 16, 5, 105000),
        (19, "Alicja", "Wróbel", "Finance", 2, 1, 68000),
        (20, "Mateusz", "Zając", "HR", 14, 4, 92000),
    ]
    cols = ["id", "first_name", "last_name", "department", "years_worked", "performance_score", "base_salary"]
    employees = pd.DataFrame(people, columns=cols)
    result = calculate_salaries(employees)
    print("SALARY CALCULATOR — 20 employees")
    print(result.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print("\nAVERAGE NET ANNUAL SALARY BY DEPARTMENT (PLN):")
    print(result.groupby("department")["net_salary"].mean().round(2).to_string())
    result.to_csv("challenge1_results.csv", index=False, encoding="utf-8-sig")
