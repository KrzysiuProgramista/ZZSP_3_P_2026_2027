import pandas as pd

df = pd.read_csv("titanic.csv")

print("1. Survival rate per class")
print(df.groupby("Pclass")["Survived"].mean(), "\n")

print("2. Survival rate per sex")
print(df.groupby("Sex")["Survived"].mean(), "\n")

print("3. Survival rate per class and sex")
print(df.groupby(["Pclass", "Sex"])["Survived"].mean(), "\n")

print("4. Average age per class")
print(df.groupby("Pclass")["Age"].mean(), "\n")

print("5. Average fare per embarkation port")
print(df.groupby("Embarked")["Fare"].mean(), "\n")

print("6. Passengers travelling alone, per class")
alone = df[(df["SibSp"] == 0) & (df["Parch"] == 0)]
print(alone.groupby("Pclass").size(), "\n")

print("7. Proportion of children per class")
children = df.assign(is_child=df["Age"] < 18).groupby("Pclass")["is_child"].mean()
print(children)
print("highest:", children.idxmax())
