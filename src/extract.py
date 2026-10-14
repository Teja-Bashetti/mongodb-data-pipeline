
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "data" / "input"
RAW_DIR = BASE_DIR / "data" / "raw"

COLLECTIONS = ["orders", "bills", "users"]


def extract_collection(collection_name):
    input_path = INPUT_DIR / f"{collection_name}.json"
    output_path = RAW_DIR / f"{collection_name}.json"

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if isinstance(records, dict):
        records = [records]

    if not isinstance(records, list):
        raise ValueError(
            f"{collection_name}.json must contain an object or list"
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    print(
        f"Extracted {len(records)} records "
        f"from {collection_name}"
    )


def main():
    for collection_name in COLLECTIONS:
        extract_collection(collection_name)

    print("Raw extraction completed successfully.")


if __name__ == "__main__":
    main()
