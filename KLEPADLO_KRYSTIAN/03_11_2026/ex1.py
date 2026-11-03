import pandas as pd

# Inna struktura inicjalizacji danych i zmienione wartości
records = [
    {"region": "West", "category": "Tech", "revenue": 1500, "quantity": 5, "unit_price": 300, "order_value": 1500},
    {"region": "West", "category": "Home", "revenue": 400, "quantity": 10, "unit_price": 40, "order_value": 400},
    {"region": "East", "category": "Tech", "revenue": 3000, "quantity": 10, "unit_price": 300, "order_value": 3000},
    {"region": "East", "category": "Home", "revenue": 800, "quantity": 20, "unit_price": 40, "order_value": 800},
    {"region": "North", "category": "Tech", "revenue": 600, "quantity": 2, "unit_price": 300, "order_value": 600},
    {"region": "North", "category": "Home", "revenue": 120, "quantity": 3, "unit_price": 40, "order_value": 120}
]
sales_df = pd.DataFrame(records)

print("--- Data ---")
print(sales_df, "\n")

# 1. Total revenue per region (zastosowanie named aggregation zamiast bezpośredniego dostępu)
res_1 = sales_df.groupby("region").agg(total_revenue=("revenue", "sum"))
print("1. Total revenue:")
print(res_1, "\n")

# 2. Average quantity per category
res_2 = sales_df.groupby("category").agg(avg_qty=("quantity", "mean"))
print("2. Avg quantity:")
print(res_2, "\n")

# 3. Number of orders per region (zwraca ramkę zamiast serii)
res_3 = sales_df.groupby("region").size().to_frame(name='orders_count')
print("3. Order count:")
print(res_3, "\n")

# 4. Revenue and average unit price per category (inne nazwy zmiennych w agregacji)
res_4 = sales_df.groupby("category").agg(
    rev_sum=("revenue", "sum"),
    price_avg=("unit_price", "mean")
)
print("4. Revenue & Avg Price:")
print(res_4, "\n")

# 5. Range of order values per region (funkcja zewnętrzna zamiast lambdy)
def calculate_range(series):
    return series.max() - series.min()

res_5 = sales_df.groupby("region")["order_value"].agg(calculate_range).to_frame(name='val_range')
print("5. Value range:")
print(res_5, "\n")