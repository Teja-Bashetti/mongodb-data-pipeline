
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

for name in ["orders", "bills", "users"]:
    file_path = RAW_DIR / f"{name}.json"

    with file_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    print(f"\n--- {name.upper()} ---")

    for index, record in enumerate(records[:1], start=1):
        print("Record:", index)
        print("Top-level fields:", list(record.keys()))

        if name == "orders":
            products = record.get("products", [])
            print("Products count:", len(products))

            if products:
                print(
                    "First product fields:",
                    list(products[0].keys())
                )

        elif name == "bills":
            items = record.get("line_items", [])
            print("Line items count:", len(items))

            if items:
                print(
                    "First line-item fields:",
                    list(items[0].keys())
                )

        elif name == "users":
            print("User fields inspected; values not printed.")
