import pandas as pd 

df = pd.read_csv("titanic.csv")

print("The survival rate per passenger class.")
print(f'{round(df.groupby("Pclass")["Survived"].mean() * 100)}%')
print("The survival rate per sex.")
print(f'{round(df.groupby("Sex")["Survived"].mean() * 100)}%')
print("The survival rate per class AND sex.")
print(f'{round(df.groupby(["Pclass", "Sex"])["Survived"].mean() * 100)}%')
print("The average age per class.")
print(round(df.groupby("Pclass")["Age"].mean()))
print("The average fare per embarkation port.")
print(round(df.groupby("Embarked")["Fare"].mean()))
print("The number of passengers per class who were travelling alone(SibSp == 0 and Parch == 0).")
alone_passangers = df[(df["SibSp"] == 0) & (df["Parch"] == 0)]
print(alone_passangers.groupby("Pclass").size())
print("The class with the highest proportion of children.")
children = df[df["Age"] < 18]
print((df["Age"] < 18).groupby(df["Pclass"]).mean().idxmax()
)