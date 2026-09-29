import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect(df):
    print(f"Shape: {df.shape}")
    print(df.dtypes)
    missing = df.isnull().sum()
    print(pd.DataFrame({'Count': missing, 'Pct (%)': (missing / len(df)) * 100}))
    print(f"Duplicates: {df.duplicated().sum()}")
    num_cols = df.select_dtypes(include='number').columns
    if not num_cols.empty:
        print(df[num_cols].agg(['min', 'max', 'mean', 'median']))
    for col in df.select_dtypes(include=['object', 'str']).columns:
        print(f"\n{col}:\nUnique: {df[col].nunique()}\nTop 3:\n{df[col].value_counts().head(3)}")

# 1. Wczytanie i inspekcja
df_titanic = pd.read_csv('titanic.csv')
inspect(df_titanic)

print("\n--- 2. 5 pytań do danych ---")
print("1. Jaki był procent przeżywalności pasażerów?")
print("2. Ile kosztował najdroższy bilet?")
print("3. Jaka była średnia wieku pasażerów?")
print("4. Czy płeć miała wpływ na szanse przeżycia?")
print("5. Ilu pasażerów podróżowało w poszczególnych klasach?")

print("\n--- 3. Odpowiedzi na 2 najprostsze pytania ---")
survival_rate = df_titanic['Survived'].mean() * 100
max_fare = df_titanic['Fare'].max()
print(f"Ad 1. Procent przeżywalności: {survival_rate:.2f}%")
print(f"Ad 2. Najdroższy bilet kosztował: {max_fare:.2f}")

print("\n--- 4. Pytania bez odpowiedzi w tym zbiorze ---")
print("1. Jakie było dokładne miejsce zamieszkania pasażera przed rejsem? (Brak danych adresowych, jest tylko port zaokrętowania).")
print("2. Jaka była bezpośrednia przyczyna śmierci osób, które zginęły (np. hipotermia, uraz mechaniczny)? (Brak raportów medycznych/wyników autopsji).")