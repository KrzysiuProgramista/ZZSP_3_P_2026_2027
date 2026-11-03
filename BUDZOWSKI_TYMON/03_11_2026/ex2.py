import pandas as pd

titanic = pd.read_csv("titanic_dataset.csv")

print(titanic.groupby("Pclass")["Survived"].mean())

print(titanic.groupby("Sex")["Survived"].mean())

print(titanic.groupby(["Pclass", "Sex"])["Survived"].mean())

print(titanic.groupby("Pclass")["Age"].mean())

print(titanic.groupby("Embarked")["Fare"].mean())

alone = titanic["SibSp"].eq(0) & titanic["Parch"].eq(0)
print(titanic.loc[alone].groupby("Pclass").size())

known_age = titanic.dropna(subset=["Age"])
child_share = known_age["Age"].lt(18).groupby(known_age["Pclass"]).mean()
print(child_share)
print(child_share.idxmax())
