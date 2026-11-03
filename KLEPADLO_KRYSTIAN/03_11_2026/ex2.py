import pandas as pd
import sys

file_path = "titanic.csv"

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku '{file_path}' w obecnym folderze.")
    sys.exit(1)

print("\n1. The survival rate per passenger class:")
print(df.groupby("Pclass")["Survived"].mean())

print("\n2. The survival rate per sex:")
print(df.groupby("Sex")["Survived"].mean())

print("\n3. The survival rate per class AND sex:")
print(df.groupby(["Pclass", "Sex"])["Survived"].mean())

print("\n4. The average age per class:")
print(df.groupby("Pclass")["Age"].mean())

print("\n5. The average fare per embarkation port:")
print(df.groupby("Embarked")["Fare"].mean())

print("\n6. Passengers per class who were travelling alone:")
print(df[(df["SibSp"] == 0) & (df["Parch"] == 0)].groupby("Pclass").size())

print("\n7. The class with the highest proportion of children:")
print((df["Age"] < 18).groupby(df["Pclass"]).mean().idxmax())



print("\nWhich passenger class had the highest survival rate?")
print(df.groupby('Pclass')['Survived'].mean().idxmax())

print("\nHow did survival differ by sex within each class?")
print(df.groupby(['Pclass', 'Sex'])['Survived'].mean())
print("\nWhich class had the highest percentage travelling alone?")
print(((df['SibSp'] == 0) & (df['Parch'] == 0)).groupby(df['Pclass']).mean().idxmax())

print("\nDoes the class with the highest average fare also have the highest survival rate?")
class_highest_fare = df.groupby('Pclass')['Fare'].mean().idxmax()
class_highest_survival = df.groupby('Pclass')['Survived'].mean().idxmax()
print(class_highest_fare == class_highest_survival)

print("\nInclude both a rate and a group size in your answer (Survival rate & size per class):")
print(df.groupby('Pclass')['Survived'].agg(survival_rate='mean', group_size='size'))