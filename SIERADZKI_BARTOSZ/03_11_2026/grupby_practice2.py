
import pandas as pd

titanic = pd.read_csv("titanic.csv")

# 1. Survival rate by passenger class
q1 = titanic.groupby("pclass").agg(
    rate=("survived", "mean"),
    size=("survived", "size")
)

print(q1)


# 2. Survival by sex within each class
q2 = titanic.groupby(["pclass", "sex"]).agg(
    rate=("survived", "mean"),
    size=("survived", "size")
)

print(q2)


# 3. Percentage travelling alone
alone = (
    titanic["sibsp"].eq(0) &
    titanic["parch"].eq(0)
)

titanic["alone"] = alone

q3 = titanic.groupby("pclass").agg(
    rate=("alone", "mean"),
    size=("alone", "size")
)

print(q3)


# 4. Average fare and survival rate
q4 = titanic.groupby("pclass").agg(
    avg_fare=("fare", "mean"),
    survival_rate=("survived", "mean"),
    size=("survived", "size")
)

print(q4)