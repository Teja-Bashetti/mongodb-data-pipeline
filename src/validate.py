
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

COLLECTIONS = ["orders", "bills", "users"]


def get_source_id(record):
    source_id = record.get("_id")

    # MongoDB Extended JSON format: {"$oid": "..."}
    if isinstance(source_id, dict):
        return source_id.get("$oid")

    # Also support string IDs
    return source_id


def validate_collection(name):
    file_path = RAW_DIR / f"{name}.json"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Raw file not found: {file_path}. Run extract.py first."
        )

    with file_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    errors = []
    seen_ids = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"Record {index}: expected a JSON object")
            continue

        source_id = get_source_id(record)

        if not source_id:
            errors.append(f"Record {index}: missing source ID")
        elif source_id in seen_ids:
            errors.append(
                f"Record {index}: duplicate source ID {source_id}"
            )
        else:
            seen_ids.add(source_id)

        if name == "orders":
            products = record.get("products", [])

            if not isinstance(products, list):
                errors.append(
                    f"Record {index}: products must be an array"
                )

        elif name == "bills":
            line_items = record.get("line_items", [])

            if not isinstance(line_items, list):
                errors.append(
                    f"Record {index}: line_items must be an array"
                )

        elif name == "users":
            user_types = record.get("user_type")

            if user_types is not None and not isinstance(user_types, list):
                errors.append(
                    f"Record {index}: user_type must be an array when present"
                )

    print(f"\n{name.upper()}")
    print(f"Records checked: {len(records)}")
    print(f"Unique IDs: {len(seen_ids)}")
    print(f"Validation errors: {len(errors)}")

    for error in errors:
        print("ERROR:", error)

    return errors


def main():
    all_errors = []

    for name in COLLECTIONS:
        all_errors.extend(validate_collection(name))

    if all_errors:
        print("\nValidation completed with errors.")
        raise SystemExit(1)

    print("\nAll validation checks passed.")


if __name__ == "__main__":
    main()
