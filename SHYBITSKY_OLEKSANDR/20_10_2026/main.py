import pandas as pd
import unittest
df = pd.read_csv('data.csv')

print(df[df['quantity'] > 10])
print("")
print(df[df["region"] == "North"])
print("")
print(df[(df["category"] == "Electronics") & (df["region"] == "North")])
print("")
print(df[df["unit_price"].between(400, 1500)])
print("")
print(df[~((df["category"] == "Electronics") & (df["region"] == "South"))])
print("")
print(df[df["region"].isin(["North", "East"]) & df["quantity"].between(5, 20)])
print("")

def validate_column(df: pd.DataFrame, column: str):
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

def filter_between(df: pd.DataFrame, column: str, low, high) -> pd.DataFrame:
    validate_column(df, column)
    return df[df[column].between(low, high)]

def filter_by_values(df: pd.DataFrame, column: str, values) -> pd.DataFrame:
    validate_column(df, column)
    return df[df[column].isin(values)]

def top_n(df: pd.DataFrame, column: str, n: int) -> pd.DataFrame:
    validate_column(df, column)
    return df.sort_values(by=column, ascending=False).head(n)


class TestFilterToolkit(unittest.TestCase):
    
    def test_filter_between(self):
        df = pd.DataFrame({"score": [10, 25, 40, 60]})
        
        res = filter_between(df, "score", 20, 50)
        self.assertEqual(len(res), 2)
        self.assertEqual(list(res["score"]), [25, 40])
        
        with self.assertRaises(ValueError):
            filter_between(df, "invalid_col", 20, 50)

    def test_filter_by_values(self):
        df = pd.DataFrame({"color": ["red", "blue", "green", "blue"]})
        
        res = filter_by_values(df, "color", ["blue", "green"])
        self.assertEqual(len(res), 3)
        
        with self.assertRaises(ValueError):
            filter_by_values(df, "missing", ["red"])

    def test_top_n(self):
        df = pd.DataFrame({"value": [5, 100, 42, 12]}).astype({"value": int})
        
        res = top_n(df, "value", 2)
        self.assertEqual(len(res), 2)
        self.assertEqual(list(res["value"]), [100, 42])
        
        with self.assertRaises(ValueError):
            top_n(df, "not_a_column", 2)

def report(df: pd.DataFrame, **filters) -> pd.DataFrame:
    total_rows_initial = len(df)
    
    for col in filters.keys():
        if col not in df.columns:
            raise ValueError(f"Unknown column: '{col}'.")
            
    filtered_df = df.copy()
    for col, val in filters.items():
        filtered_df = filtered_df[filtered_df[col] == val]
        
    matched_rows = len(filtered_df)
    print(f"Matched rows / total rows: {matched_rows} / {total_rows_initial}")
    
    if "sales-value" in filtered_df.columns:
        total_sales_value = filtered_df["sales-value"].sum()
    elif "quantity" in filtered_df.columns and "unit_price" in filtered_df.columns:
        total_sales_value = (filtered_df["quantity"] * filtered_df["unit_price"]).sum()
    else:
        total_sales_value = 0.0
        
    print(f"Total sales value: {total_sales_value}")
    
    return filtered_df

print(report(df, region="North", category="Electronics"))


if __name__ == "__main__":
    unittest.main()