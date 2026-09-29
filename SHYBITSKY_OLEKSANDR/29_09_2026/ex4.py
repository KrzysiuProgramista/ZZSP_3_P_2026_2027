import json
from pathlib import Path
import pandas as pd


def main() -> None:
    data_dir = Path(".")
    json_path = data_dir / "products.json"

    df_raw = pd.read_json(json_path, encoding="utf-8")

    print("=== 1. Standard pd.read_json() ===")
    print(df_raw)
    print("\nData Types:")
    print(df_raw.dtypes)

    print(
        "\nNote: Column 'supplier' contains dictionary objects:",
        type(df_raw["supplier"].iloc[0]),
    )

    with open(json_path, "r", encoding="utf-8") as f:
        data_dict = json.load(f)

    df_normalized = pd.json_normalize(data_dict)

    print("\n=== 2. Flattened with pd.json_normalize() ===")
    print(df_normalized)

    print("\n=== Comparison ===")
    print(f"Raw DF columns: {df_raw.columns.tolist()}")
    print(f"Normalized DF columns: {df_normalized.columns.tolist()}")


if __name__ == "__main__":
    main()