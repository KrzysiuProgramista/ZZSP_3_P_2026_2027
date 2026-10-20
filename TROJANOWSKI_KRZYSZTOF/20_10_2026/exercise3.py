import pandas as pa

def report(df, **filters):
    for column in filters:
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")
    
    result = df
    for column, value in filters.items():
        result = result[result[column] == value]

    print(f"Matched rows: {len(result)} / {len(df)}")

    return result


df = pa.read_csv("data.csv")
print(report(df, unit_price=1200, region="North"))