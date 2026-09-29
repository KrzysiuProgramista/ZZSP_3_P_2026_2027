import time
from pathlib import Path
import pandas as pd

def main():
    data_dir = Path(".")
    csv_path = data_dir / "sales.csv"

    start_full = time.perf_counter()
    df_full = pd.read_csv(csv_path, encoding="utf-8")
    end_full = time.perf_counter()
    time_full = end_full - start_full

    start_partial = time.perf_counter()
    df_partial = pd.read_csv(
        csv_path,
        usecols=["date", "product", "quantity"],
        nrows=10,
        encoding="utf-8",
    )
    end_partial = time.perf_counter()
    time_partial = end_partial - start_partial

    print("Full file load shape:", df_full.shape)
    print("Full file load time:", f"{time_full:.6f} seconds")
    print("Optimized load shape:", df_partial.shape)
    print("Optimized load time:", f"{time_partial:.6f} seconds")
    print(df_partial.head(10))

if __name__ == "__main__":
    main()