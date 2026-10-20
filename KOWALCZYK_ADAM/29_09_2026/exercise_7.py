import pandas as pd

# Kopia funkcji inspect z Zadania 3 (Dodane, aby plik był kompletny)
def inspect(df):
    print("--- Shape ---")
    print(df.shape)
    print("\n--- Columns and Dtypes ---")
    print(df.dtypes)
    print("\n--- Missing Values (Count & Percentage) ---")
    missing = pd.isna(df).sum()
    missing_pct = pd.isna(df).mean() * 100
    print(pd.DataFrame({"count": missing, "percentage": missing_pct}))
    print("\n--- Duplicate Rows ---")
    print("Total duplicates:", df.duplicated().sum())
    print("\n--- Numeric Columns Summary ---")
    print(df.describe())
    print("\n--- Object Columns Summary ---")
    for col in df.columns:
        if df[col].dtype == "object":
            print(f"\nColumn: {col}")
            print(f"Unique values: {df[col].nunique()}")
            print(f"Top 3 common:\n{df[col].value_counts().head(3)}")

# Exercise 7: An unfamiliar dataset
titanic_df = pd.read_csv("titanic.csv")

# Inspekcja danych (Dodane)
print("====== INSPECTING titanic.csv ======")
inspect(titanic_df)

print("\n--- 5 Questions we could answer ---")
print("1. What was the overall survival rate?")
print("2. How did survival rate differ by sex?")
print("3. Did passenger class affect survival chances?")
print("4. What was the average age of the passengers?")
print("5. How much did the fares vary across different classes?")

print("\n--- Answering the 2 easiest ones ---")
# Q1: Overall survival rate
overall_survival = titanic_df["Survived"].mean()
print(f"1. Overall survival rate: {overall_survival:.1%}")

# Q2: Survival rate by sex
survival_by_sex = titanic_df.groupby("Sex")["Survived"].mean()
print(f"2. Survival rate by sex:\n{survival_by_sex}")

print("\n--- 2 Questions we CANNOT answer ---")
print("1. What was the exact cause of death for each passenger? (Missing: medical records/autopsy data)")
print("2. Did passengers in cabin C85 have a window? (Missing: detailed ship floorplans and cabin features)")