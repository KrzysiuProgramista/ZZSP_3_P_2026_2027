import pandas as pd

df = pd.read_csv("Titanic-Dataset.csv")

# 1. Survival rate per class
print(df.groupby("Pclass")["Survived"].mean())

# 2. Survival rate per sex
print(df.groupby("Sex")["Survived"].mean())

# 3. Survival rate per class AND sex
print(df.groupby(["Pclass", "Sex"])["Survived"].mean())

# 4. Average age per class
print(df.groupby("Pclass")["Age"].mean())

# 5. Average fare per embarkation port
print(df.groupby("Embarked")["Fare"].mean())

# 6. Travelling alone, count per class
print(df[(df.SibSp == 0) & (df.Parch == 0)].groupby("Pclass").size())

# 7. Class with the highest proportion of children (Age < 18)
print((df["Age"] < 18).groupby(df["Pclass"]).mean().idxmax())