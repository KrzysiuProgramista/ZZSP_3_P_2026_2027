"""
Titanic dataset — groupby exercise.
Dataset: https://www.kaggle.com/datasets/yasserh/titanic-dataset
Each answer is a single groupby expression.
"""
import pandas as pd

df = pd.read_csv("Titanic-Dataset.csv")

# 1. Survival rate per passenger class.
print("1. Survival rate per class:")
print(df.groupby("Pclass")["Survived"].mean())

# 2. Survival rate per sex.
print("\n2. Survival rate per sex:")
print(df.groupby("Sex")["Survived"].mean())

# 3. Survival rate per class AND sex.
print("\n3. Survival rate per class and sex:")
print(df.groupby(["Pclass", "Sex"])["Survived"].mean())

# 4. Average age per class.
print("\n4. Average age per class:")
print(df.groupby("Pclass")["Age"].mean())

# 5. Average fare per embarkation port.
print("\n5. Average fare per embarkation port:")
print(df.groupby("Embarked")["Fare"].mean())

# 6. Number of passengers per class travelling alone (SibSp == 0 and Parch == 0).
print("\n6. Passengers travelling alone per class:")
print(df[(df["SibSp"] == 0) & (df["Parch"] == 0)].groupby("Pclass").size())

# 7. The class with the highest proportion of children (Age < 18).
print("\n7. Class with the highest proportion of children:")
print(df.assign(is_child=df["Age"] < 18).groupby("Pclass")["is_child"].mean().idxmax())
