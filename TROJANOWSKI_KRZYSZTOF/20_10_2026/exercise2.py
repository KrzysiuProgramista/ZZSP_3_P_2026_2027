import pandas as pa



df = pa.read_csv("data.csv")

#1
def filter_between(df, column, low, high):
    if(column not in df.columns):
        raise ValueError("Not in columns")

    return df[column].between(low, high)

print(df[filter_between(df, "unit_price", 5, 100)])

#2
def filter_by_value(df, column, values):
    if(column not in df.columns):
        raise ValueError("Not in columns")
    return df[column].isin(values)

print(df[filter_by_value(df, "unit_price", [1200])])

#3 
def top_n(df, column, n):
    if(column not in df.columns):
        raise ValueError("Not in columns")
    return df.sort_values(by=column).head(n)

print(top_n(df, "unit_price", 5))