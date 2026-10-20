# Exercise 7: An unfamiliar dataset

Dataset: Titanic Dataset  
Source: https://www.kaggle.com/datasets/yasserh/titanic-dataset

## 1. Run `inspect()` on the dataset

```python
import pandas as pd

df = pd.read_csv("Titanic-Dataset.csv")
inspect(df)
```

The dataset contains **891 rows and 12 columns**:

- `PassengerId`
- `Survived`
- `Pclass`
- `Name`
- `Sex`
- `Age`
- `SibSp`
- `Parch`
- `Ticket`
- `Fare`
- `Cabin`
- `Embarked`

Some columns contain missing values, especially `Cabin` and `Age`.

## 2. Five questions that can be answered with this data

1. How many passengers survived the Titanic disaster?
2. What percentage of passengers survived?
3. Did women have a higher survival rate than men?
4. Did passengers in first class survive more often than passengers in third class?
5. What was the average age of the passengers?

## 3. Answer the two easiest questions

### Question 1: How many passengers survived?

```python
df["Survived"].value_counts()
```

Result:

- **342 passengers survived**.
- **549 passengers did not survive**.

### Question 2: What percentage of passengers survived?

```python
survival_rate = df["Survived"].mean() * 100
print(round(survival_rate, 2))
```

Result:

- About **38.38%** of the passengers survived.

## 4. Two questions that cannot be answered with this dataset

### Question 1: Why did a particular passenger survive or die?

The dataset shows whether a passenger survived, but it does not contain detailed information about the passenger's exact location during the accident, access to a lifeboat, injuries, or decisions made during the evacuation.

**Missing data:** lifeboat assignment, evacuation route, exact location on the ship, injuries, and detailed events during the sinking.

### Question 2: What happened to the passengers after the disaster?

The dataset ends with information about the Titanic journey and survival status. It does not include information about the survivors' later lives.

**Missing data:** later residence, occupation, health, family situation, and other post-disaster information.
