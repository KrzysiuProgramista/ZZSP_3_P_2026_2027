import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Put the CSV downloaded from the exercise's Kaggle page here.
# The script accepts either Titanic-Dataset.csv or titanic.csv.
possible_files = [
    BASE_DIR / "Titanic-Dataset.csv",
    BASE_DIR / "titanic.csv",
]

titanic_path = next((p for p in possible_files if p.exists()), None)

if titanic_path is None:
    raise FileNotFoundError(
        "Download the Titanic Dataset CSV from the exercise's Kaggle page "
        "and save it as Titanic-Dataset.csv in the project folder."
    )

titanic_df = pd.read_csv(titanic_path)

def inspect(df):
    print("=" * 60)
    print("Shape:", df.shape)

    print("\nColumns and dtypes:")
    for column, dtype in df.dtypes.items():
        print(f"  {column}: {dtype}")

    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percent": (df.isna().mean() * 100).round(2)
    })
    print("\nMissing values:")
    print(missing)

    print("\nDuplicate rows:", df.duplicated().sum())

    numeric_columns = df.select_dtypes(include="number").columns
    if len(numeric_columns):
        print("\nNumeric columns:")
        print(pd.DataFrame({
            "min": df[numeric_columns].min(),
            "max": df[numeric_columns].max(),
            "mean": df[numeric_columns].mean(),
            "median": df[numeric_columns].median()
        }))

    object_columns = df.select_dtypes(include="object").columns
    print("\nObject columns:")
    for column in object_columns:
        print(f"\n{column}:")
        print("  unique values:", df[column].nunique(dropna=True))
        print("  3 most common:")
        print(df[column].value_counts(dropna=True).head(3))

print("=== 1. inspect(titanic_df) ===")
inspect(titanic_df)

print("\n=== 2. Five questions ===")
questions = [
    "1. How many passengers survived?",
    "2. What percentage of passengers survived?",
    "3. How does survival differ by passenger class?",
    "4. How does survival differ by sex?",
    "5. What is the average age of passengers?"
]
print("\n".join(questions))

print("\n=== 3. Two easiest questions ===")
survived_count = int(titanic_df["Survived"].sum())
survival_percent = titanic_df["Survived"].mean() * 100
print(f"1. Number of survivors: {survived_count}")
print(f"2. Survival percentage: {survival_percent:.2f}%")

print("\n=== 4. Questions that cannot be answered ===")
print("1. What was each passenger's exact medical condition?")
print("   Missing data: medical records/health information.")
print("2. What happened to each passenger after the Titanic disaster?")
print("   Missing data: post-disaster records or later-life records.")
