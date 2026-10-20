"""01 - Exercises 6 to 8: selective reading, an unfamiliar dataset, a messy import.

Worked solutions. See README.md for the task descriptions.
Run with:  python exercises_6_8.py
"""

import time

import pandas as pd

from exercises import header, inspect

BIG = "sales_large.csv"   # 300,000 rows - sales.csv is too small to time


# --- Exercise 6: only what you need --------------------------------------

def timed(label, fn):
    """Run fn a few times, report the best wall-clock time and the shape."""
    best = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        result = fn()
        best = min(best, time.perf_counter() - start)
    print(f"  {label:<38} {best * 1000:7.1f} ms   shape={result.shape}")
    return result


def exercise_6():
    header("EXERCISE 6 - only what you need")

    # 1. Three columns instead of all seven.
    subset = pd.read_csv(BIG, usecols=["date", "product", "amount"])
    print("usecols - columns read:", list(subset.columns))
    print(subset.head(3), "\n")

    # 2. Ten rows instead of all 300,000.
    first_10 = pd.read_csv(BIG, nrows=10)
    print(f"nrows=10 -> {first_10.shape[0]} rows\n")

    # 3. What each one costs. perf_counter is the script equivalent of
    #    %timeit; best-of-3 because the first read warms the OS file cache.
    print("Timings (best of 3):")
    timed("everything", lambda: pd.read_csv(BIG))
    timed("usecols=[date, product, amount]",
          lambda: pd.read_csv(BIG, usecols=["date", "product", "amount"]))
    timed("nrows=10", lambda: pd.read_csv(BIG, nrows=10))
    timed("usecols + parse_dates",
          lambda: pd.read_csv(BIG, usecols=["date", "product", "amount"],
                              parse_dates=["date"]))

    print("\nusecols saves both time and memory - the parser never builds\n"
          "the columns you left out. nrows stops after n lines, so it is\n"
          "near-instant whatever the file size: the right way to peek at a\n"
          "file before committing to reading all of it.")

    return subset


# --- Exercise 7: an unfamiliar dataset -----------------------------------

def exercise_7():
    header("EXERCISE 7 - Titanic")

    titanic = pd.read_csv("titanic.csv")
    inspect(titanic, "titanic")

    print("""
FIVE QUESTIONS THIS DATA CAN ANSWER
  1. What share of passengers survived?
  2. Did survival rate differ by sex?
  3. Did survival rate differ by passenger class?
  4. Were survivors younger on average than non-survivors?
  5. Did passengers travelling with family survive more often than
     those travelling alone? (SibSp + Parch)

THE TWO EASIEST, ANSWERED BELOW: (1) and (2).""")

    rate = titanic["Survived"].mean()
    print(f"\n  Q1  Overall survival: {rate:.1%} "
          f"({titanic['Survived'].sum()} of {len(titanic)})")

    by_sex = titanic.groupby("Sex")["Survived"].agg(["mean", "count"])
    print("\n  Q2  Survival by sex:")
    for sex, row in by_sex.iterrows():
        print(f"        {sex:<8} {row['mean']:.1%}  (n={int(row['count'])})")
    print("      Women survived at roughly four times the rate of men.")

    # Free extras, since they are one line each:
    by_class = titanic.groupby("Pclass")["Survived"].mean()
    print("\n  Bonus, Q3 survival by class:")
    for pclass, r in by_class.items():
        print(f"        class {pclass}  {r:.1%}")

    print("""
TWO QUESTIONS THIS DATA CANNOT ANSWER
  A. "Did being near a lifeboat station improve your odds?"
     Missing: each passenger's cabin location as a deck/section the ship
     plan can be joined against, plus where the boats were. Cabin is
     ~77% missing here, and even when present it is a room number with
     no deck layout to resolve it against.

  B. "Did passengers who could swim survive more often?"
     Missing: swimming ability was never recorded for anyone. No amount
     of cleaning recovers a variable that was not collected - the honest
     answer is that this question needs a different dataset, not better
     analysis of this one.

  Worth noting for both: this file has 891 rows, not the ~2,224 people
  aboard. It is a sample, so every rate above describes these 891
  passengers, not the Titanic as a whole.""")

    return titanic


# --- Exercise 8: the messy import ----------------------------------------

def exercise_8():
    header("EXERCISE 8 - messy.csv")

    print("Raw file:")
    with open("messy.csv") as f:
        print("".join(f"  {line}" for line in f))

    messy = (
        pd.read_csv(
            "messy.csv",
            sep=";",                              # semicolon separated
            comment="#",                          # drops the two junk lines
            na_values=["n/a", "-", "brak", ""],   # all four missing markers
            dayfirst=True,                        # 05.01.2026 = 5 January
            parse_dates=["order_date"],
        )
        .assign(price=lambda d: pd.to_numeric(
            d["price"].str.removesuffix(" PLN")   # "3 500,00 PLN" -> "3 500,00"
                      .str.replace(" ", "", regex=False)   # thousands separator
                      .str.replace(",", ".", regex=False),  # decimal comma
            errors="coerce"))
        .astype({"quantity": "Int64"})            # nullable int, not float
        .drop_duplicates()
    )

    print("Clean result:")
    print(messy.to_string(index=False))
    print("\nDtypes:")
    print(messy.dtypes)
    print(f"\nRows: 9 in the file -> {len(messy)} after drop_duplicates()")
    print(f"\nMissing values per column:\n{messy.isna().sum().to_string()}")

    print("""
WHY EACH PARAMETER
  sep=";"            the file is semicolon separated, not comma.
  comment="#"        everything after # on a line is ignored, so the two
                     banner lines vanish and row 3 becomes the header.
                     Safer than skiprows=2 - it does not break if the
                     export adds a third comment line next month.
  na_values=[...]    "n/a", "-" and "brak" are this system's ways of
                     writing nothing. Empty cells are already NaN, but
                     listing "" costs nothing and documents the intent.
                     Declaring them here, rather than fixing them later,
                     is what lets quantity parse straight to a number.
  dayfirst=True      05.01.2026 is 5 January, not 1 May. Without this
                     pandas guesses, and it guesses US-style.
  parse_dates=[...]  order_date becomes datetime64 instead of text.

  Note what is NOT in that list: thousands=" " and decimal=",". They look
  like the right tools, but they only apply to columns pandas is already
  parsing as numeric. price contains " PLN", so it arrives as text and
  those two parameters never touch it - setting them silently does
  nothing here. The price column has to be cleaned by hand instead:
  drop the suffix, drop the thousands space, swap the decimal comma for
  a dot, then to_numeric with errors="coerce" so the "-" row becomes NaN
  rather than raising.

  astype({"quantity": "Int64"})  - capital-I Int64 is the nullable
  integer type. Plain int64 cannot hold the missing quantity on row 2,
  which is why pandas made the column float64 by default; quantities of
  3.0 and 40.0 are ugly and invite rounding bugs later.

  drop_duplicates() removes the exact repeat of id=4. Note it keeps the
  two Mouse rows - different id, quantity and date, so they are two real
  orders, not a duplicate. Dropping on a subset like ["id"] would be the
  stricter choice if ids must be unique.""")

    return messy


if __name__ == "__main__":
    exercise_6()
    exercise_7()
    exercise_8()
