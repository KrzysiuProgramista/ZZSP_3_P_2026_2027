import pandas as pd

titanic = pd.read_csv("Titanic-Dataset.csv")

print("1. Survival rate per class")
print(titanic.groupby("Pclass")["Survived"].mean(), "\n")

print("2. Survival rate per sex")
print(titanic.groupby("Sex")["Survived"].mean(), "\n")

print("3. Survival rate per class and sex")
print(titanic.groupby(["Pclass", "Sex"])["Survived"].mean(), "\n")

print("4. Average age per class")
print(titanic.groupby("Pclass")["Age"].mean(), "\n")

print("5. Average fare per port")
print(titanic.groupby("Embarked")["Fare"].mean(), "\n")

print("6. Passengers travelling alone per class")
print(titanic[(titanic["SibSp"] == 0) & (titanic["Parch"] == 0)].groupby("Pclass").size(), "\n")

print("7. Class with highest proportion of children")
print(titanic.dropna(subset=["Age"]).assign(is_child=lambda d: d["Age"] < 18).groupby("Pclass")["is_child"].mean())