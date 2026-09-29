from pathlib import Path
import pandas as pd
from ex3 import inspect

def main():
    data_dir = Path(".")
    titanic_path = data_dir / "titanic.csv"

    if not titanic_path.is_file():
        print(f"File {titanic_path} not found. Please place titanic.csv in the working directory.")
        return

    titanic_df = pd.read_csv(titanic_path, encoding="utf-8")

    inspect(titanic_df)

    pclass_survival = titanic_df.groupby("Pclass")["Survived"].mean() * 100
    print("Survival rate by passenger class (%):")
    print(pclass_survival.round(2))
    print()

    gender_counts = titanic_df["Sex"].value_counts()
    print("Passenger count by gender:")
    print(gender_counts)

if __name__ == "__main__":
    main()

'''
Five questions you could answer with this data:

1. What was the survival rate of passengers based on their ticket class (Pclass)?
2. How many male and female passengers were on board (Sex)?
3. What was the average age of passengers who survived versus those who did not?
4. What was the average ticket fare (Fare) across different passenger classes?
5. How many passengers traveled with family members (sum of SibSp and Parch)?

Answers to the two easiest questions:

Question 1 (Survival rate by class): First-class passengers had the highest survival rate (~62.96%), followed by second-class (~47.28%), and third-class passengers had the lowest survival rate (~24.24%).
Question 2 (Passenger count by gender): There were 577 male passengers and 314 female passengers on board.

Two questions you CANNOT answer (and the missing data):

1. Did passengers who spoke English have a higher chance of being saved?
2. Missing data: Information about passengers' spoken languages, primary language, or nationality is not included in the dataset.
3. At what time and in what order did the lifeboats launch from the ship?

Missing data: Lifeboat numbers, evacuation timestamps, and passenger lifeboat assignment records are missing.'''